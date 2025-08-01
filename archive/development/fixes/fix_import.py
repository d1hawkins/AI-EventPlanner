with open('app/web/router.py', 'r') as f:
    content = f.read()

content = content.replace('from app.graphs.coordinator_graph import create_coordinator_graph create_initial_state', 
                         'from app.graphs.coordinator_graph import create_coordinator_graph, create_initial_state')

with open('app/web/router.py', 'w') as f:
    f.write(content)

print("File updated successfully.")
