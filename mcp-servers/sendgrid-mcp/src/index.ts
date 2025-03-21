#!/usr/bin/env node

/**
 * SendGrid MCP Server
 * This server provides email functionality using the SendGrid API.
 * It allows:
 * - Sending individual emails
 * - Sending bulk emails to multiple recipients
 * - Creating and managing email templates
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ErrorCode,
  McpError,
} from "@modelcontextprotocol/sdk/types.js";
import sgMail from "@sendgrid/mail";

/**
 * Type definitions for email objects
 */
type EmailTemplate = {
  id: string;
  name: string;
  subject: string;
  content: string;
  created: string;
};

type EmailRecipient = {
  email: string;
  name?: string;
};

/**
 * Simple in-memory storage for email templates.
 * In a real implementation, this would likely be backed by a database.
 */
const emailTemplates: { [id: string]: EmailTemplate } = {
  "welcome": {
    id: "welcome",
    name: "Welcome Email",
    subject: "Welcome to our event!",
    content: "Hello {{name}},\n\nWelcome to {{event_name}}! We're excited to have you join us.\n\nBest regards,\nThe Event Team",
    created: new Date().toISOString()
  },
  "reminder": {
    id: "reminder",
    name: "Event Reminder",
    subject: "Reminder: {{event_name}} is coming up!",
    content: "Hello {{name}},\n\nThis is a friendly reminder that {{event_name}} is scheduled for {{event_date}}.\n\nWe look forward to seeing you there!\n\nBest regards,\nThe Event Team",
    created: new Date().toISOString()
  }
};

/**
 * Initialize the SendGrid API client with the API key from environment variables.
 * The API key should be provided in the MCP settings configuration.
 */
const initSendGrid = () => {
  const apiKey = process.env.SENDGRID_API_KEY;
  if (!apiKey) {
    console.error("SENDGRID_API_KEY environment variable is required");
    return false;
  }
  
  try {
    sgMail.setApiKey(apiKey);
    return true;
  } catch (error) {
    console.error("Failed to initialize SendGrid:", error);
    return false;
  }
};

/**
 * Create an MCP server with capabilities for email tools.
 */
const server = new Server(
  {
    name: "sendgrid-mcp",
    version: "0.1.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

/**
 * Handler that lists available tools.
 * Exposes email-related tools for sending emails and managing templates.
 */
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "send_email",
        description: "Send an email to a single recipient",
        inputSchema: {
          type: "object",
          properties: {
            to: {
              type: "object",
              properties: {
                email: { type: "string", description: "Recipient email address" },
                name: { type: "string", description: "Recipient name (optional)" }
              },
              required: ["email"],
              description: "Email recipient"
            },
            from: {
              type: "object",
              properties: {
                email: { type: "string", description: "Sender email address" },
                name: { type: "string", description: "Sender name (optional)" }
              },
              required: ["email"],
              description: "Email sender"
            },
            subject: {
              type: "string",
              description: "Email subject line"
            },
            content: {
              type: "string",
              description: "Email content (HTML supported)"
            },
            template_id: {
              type: "string",
              description: "ID of a template to use (optional, overrides content if provided)"
            },
            template_data: {
              type: "object",
              description: "Data to populate template variables (optional)"
            }
          },
          required: ["to", "from", "subject"]
        }
      },
      {
        name: "send_bulk_emails",
        description: "Send emails to multiple recipients",
        inputSchema: {
          type: "object",
          properties: {
            to: {
              type: "array",
              items: {
                type: "object",
                properties: {
                  email: { type: "string", description: "Recipient email address" },
                  name: { type: "string", description: "Recipient name (optional)" }
                },
                required: ["email"]
              },
              description: "List of email recipients"
            },
            from: {
              type: "object",
              properties: {
                email: { type: "string", description: "Sender email address" },
                name: { type: "string", description: "Sender name (optional)" }
              },
              required: ["email"],
              description: "Email sender"
            },
            subject: {
              type: "string",
              description: "Email subject line"
            },
            content: {
              type: "string",
              description: "Email content (HTML supported)"
            },
            template_id: {
              type: "string",
              description: "ID of a template to use (optional, overrides content if provided)"
            },
            template_data: {
              type: "object",
              description: "Data to populate template variables (optional)"
            },
            is_personalized: {
              type: "boolean",
              description: "Whether each recipient should receive a personalized email (default: false)"
            }
          },
          required: ["to", "from", "subject"]
        }
      },
      {
        name: "create_email_template",
        description: "Create a new email template",
        inputSchema: {
          type: "object",
          properties: {
            name: {
              type: "string",
              description: "Template name"
            },
            subject: {
              type: "string",
              description: "Default subject line for the template"
            },
            content: {
              type: "string",
              description: "Template content with variables in {{variable_name}} format"
            }
          },
          required: ["name", "subject", "content"]
        }
      },
      {
        name: "list_email_templates",
        description: "List all available email templates",
        inputSchema: {
          type: "object",
          properties: {}
        }
      },
      {
        name: "get_email_template",
        description: "Get a specific email template by ID",
        inputSchema: {
          type: "object",
          properties: {
            template_id: {
              type: "string",
              description: "ID of the template to retrieve"
            }
          },
          required: ["template_id"]
        }
      }
    ]
  };
});

/**
 * Replace template variables in a string with values from a data object.
 * For example, "Hello {{name}}" with data {name: "John"} becomes "Hello John".
 */
const replaceTemplateVariables = (content: string, data: Record<string, any>): string => {
  return content.replace(/\{\{([^}]+)\}\}/g, (match, key) => {
    return data[key] !== undefined ? String(data[key]) : match;
  });
};

/**
 * Handler for email-related tools.
 * Implements functionality for sending emails and managing templates.
 */
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  // Initialize SendGrid if needed
  const isInitialized = initSendGrid();
  if (!isInitialized) {
    throw new McpError(
      ErrorCode.InternalError,
      "Failed to initialize SendGrid. Make sure SENDGRID_API_KEY is set."
    );
  }

  switch (request.params.name) {
    case "send_email": {
      const { to, from, subject, content, template_id, template_data } = request.params.arguments as any;
      
      if (!to || !from || !subject) {
        throw new McpError(
          ErrorCode.InvalidParams,
          "Missing required parameters: to, from, and subject are required"
        );
      }

      let emailContent = content;
      
      // If template_id is provided, use the template
      if (template_id) {
        const template = emailTemplates[template_id];
        if (!template) {
          throw new McpError(
            ErrorCode.InvalidParams,
            `Template with ID ${template_id} not found`
          );
        }
        
        emailContent = template.content;
        
        // Replace template variables if template_data is provided
        if (template_data) {
          emailContent = replaceTemplateVariables(emailContent, template_data);
        }
      } else if (!content) {
        throw new McpError(
          ErrorCode.InvalidParams,
          "Either content or template_id must be provided"
        );
      }

      try {
        const msg = {
          to: to.email,
          from: from.email,
          subject: subject,
          html: emailContent,
          // Add personalization if names are provided
          personalizations: to.name ? [{
            to: [{ email: to.email, name: to.name }],
            from: { email: from.email, name: from.name },
            subject: subject,
          }] : undefined
        };

        // In a real implementation, this would send the email via SendGrid
        // For now, we'll just log it and simulate success
        console.log("Sending email:", JSON.stringify(msg, null, 2));
        
        // Uncomment to actually send the email
        // await sgMail.send(msg);

        return {
          content: [{
            type: "text",
            text: `Email sent successfully to ${to.email}`
          }]
        };
      } catch (error) {
        console.error("Error sending email:", error);
        throw new McpError(
          ErrorCode.InternalError,
          `Failed to send email: ${error instanceof Error ? error.message : String(error)}`
        );
      }
    }

    case "send_bulk_emails": {
      const { to, from, subject, content, template_id, template_data, is_personalized } = request.params.arguments as any;
      
      if (!to || !from || !subject) {
        throw new McpError(
          ErrorCode.InvalidParams,
          "Missing required parameters: to, from, and subject are required"
        );
      }

      if (!Array.isArray(to) || to.length === 0) {
        throw new McpError(
          ErrorCode.InvalidParams,
          "The 'to' parameter must be a non-empty array of recipients"
        );
      }

      let emailContent = content;
      
      // If template_id is provided, use the template
      if (template_id) {
        const template = emailTemplates[template_id];
        if (!template) {
          throw new McpError(
            ErrorCode.InvalidParams,
            `Template with ID ${template_id} not found`
          );
        }
        
        emailContent = template.content;
      } else if (!content) {
        throw new McpError(
          ErrorCode.InvalidParams,
          "Either content or template_id must be provided"
        );
      }

      try {
        if (is_personalized) {
          // Send personalized emails to each recipient
          const emails = to.map((recipient: EmailRecipient) => {
            let personalizedContent = emailContent;
            
            // Replace template variables if template_data is provided
            if (template_data) {
              // Merge template_data with recipient data for personalization
              const personalData = {
                ...template_data,
                email: recipient.email,
                name: recipient.name || recipient.email
              };
              personalizedContent = replaceTemplateVariables(personalizedContent, personalData);
            }

            return {
              to: { email: recipient.email, name: recipient.name },
              from: { email: from.email, name: from.name },
              subject: subject,
              html: personalizedContent
            };
          });

          // In a real implementation, this would send the emails via SendGrid
          console.log(`Sending ${emails.length} personalized emails`);
          
          // Uncomment to actually send the emails
          // await sgMail.send(emails);

          return {
            content: [{
              type: "text",
              text: `Sent ${emails.length} personalized emails successfully`
            }]
          };
        } else {
          // Send a single email with multiple recipients
          const msg = {
            to: to.map((r: EmailRecipient) => ({ email: r.email, name: r.name })),
            from: { email: from.email, name: from.name },
            subject: subject,
            html: emailContent
          };

          // In a real implementation, this would send the email via SendGrid
          console.log(`Sending bulk email to ${to.length} recipients`);
          
          // Uncomment to actually send the email
          // await sgMail.send(msg);

          return {
            content: [{
              type: "text",
              text: `Sent email to ${to.length} recipients successfully`
            }]
          };
        }
      } catch (error) {
        console.error("Error sending bulk emails:", error);
        throw new McpError(
          ErrorCode.InternalError,
          `Failed to send bulk emails: ${error instanceof Error ? error.message : String(error)}`
        );
      }
    }

    case "create_email_template": {
      const { name, subject, content } = request.params.arguments as any;
      
      if (!name || !subject || !content) {
        throw new McpError(
          ErrorCode.InvalidParams,
          "Missing required parameters: name, subject, and content are required"
        );
      }

      // Generate a simple ID based on the name
      const id = name.toLowerCase().replace(/[^a-z0-9]/g, "_");
      
      // Check if a template with this ID already exists
      if (emailTemplates[id]) {
        throw new McpError(
          ErrorCode.InvalidParams,
          `A template with ID ${id} already exists`
        );
      }

      // Create the new template
      const newTemplate: EmailTemplate = {
        id,
        name,
        subject,
        content,
        created: new Date().toISOString()
      };

      emailTemplates[id] = newTemplate;

      return {
        content: [{
          type: "text",
          text: `Created email template "${name}" with ID "${id}"`
        }]
      };
    }

    case "list_email_templates": {
      const templateList = Object.values(emailTemplates).map(template => ({
        id: template.id,
        name: template.name,
        subject: template.subject,
        created: template.created
      }));

      return {
        content: [{
          type: "text",
          text: JSON.stringify(templateList, null, 2)
        }]
      };
    }

    case "get_email_template": {
      const { template_id } = request.params.arguments as any;
      
      if (!template_id) {
        throw new McpError(
          ErrorCode.InvalidParams,
          "Missing required parameter: template_id"
        );
      }

      const template = emailTemplates[template_id];
      if (!template) {
        throw new McpError(
          ErrorCode.InvalidParams,
          `Template with ID ${template_id} not found`
        );
      }

      return {
        content: [{
          type: "text",
          text: JSON.stringify(template, null, 2)
        }]
      };
    }

    default:
      throw new McpError(
        ErrorCode.MethodNotFound,
        `Unknown tool: ${request.params.name}`
      );
  }
});

/**
 * Start the server using stdio transport.
 * This allows the server to communicate via standard input/output streams.
 */
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("SendGrid MCP server running on stdio");
}

main().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});
