import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ProgressBar } from './ProgressBar';

describe('ProgressBar Component', () => {
  describe('Rendering', () => {
    it('should render progress bar', () => {
      const { container } = render(<ProgressBar progress={50} />);
      const progressBar = container.querySelector('.h-2');

      expect(progressBar).toBeInTheDocument();
    });

    it('should set correct width based on progress', () => {
      const { container } = render(<ProgressBar progress={75} />);
      const progressFill = container.querySelector('.h-full');

      expect(progressFill).toHaveStyle({ width: '75%' });
    });

    it('should render with 0% progress', () => {
      const { container } = render(<ProgressBar progress={0} />);
      const progressFill = container.querySelector('.h-full');

      expect(progressFill).toHaveStyle({ width: '0%' });
    });

    it('should render with 100% progress', () => {
      const { container } = render(<ProgressBar progress={100} />);
      const progressFill = container.querySelector('.h-full');

      expect(progressFill).toHaveStyle({ width: '100%' });
    });
  });

  describe('Color Classes', () => {
    it('should apply danger color for progress < 25', () => {
      const { container } = render(<ProgressBar progress={20} />);
      const progressFill = container.querySelector('.h-full');

      expect(progressFill).toHaveClass('bg-danger');
    });

    it('should apply warning color for progress 25-49', () => {
      const { container } = render(<ProgressBar progress={40} />);
      const progressFill = container.querySelector('.h-full');

      expect(progressFill).toHaveClass('bg-warning');
    });

    it('should apply primary color for progress 50-79', () => {
      const { container } = render(<ProgressBar progress={60} />);
      const progressFill = container.querySelector('.h-full');

      expect(progressFill).toHaveClass('bg-primary');
    });

    it('should apply success color for progress >= 80', () => {
      const { container } = render(<ProgressBar progress={85} />);
      const progressFill = container.querySelector('.h-full');

      expect(progressFill).toHaveClass('bg-success');
    });

    it('should apply correct color at boundary (25)', () => {
      const { container } = render(<ProgressBar progress={25} />);
      const progressFill = container.querySelector('.h-full');

      expect(progressFill).toHaveClass('bg-warning');
    });

    it('should apply correct color at boundary (50)', () => {
      const { container } = render(<ProgressBar progress={50} />);
      const progressFill = container.querySelector('.h-full');

      expect(progressFill).toHaveClass('bg-primary');
    });

    it('should apply correct color at boundary (80)', () => {
      const { container } = render(<ProgressBar progress={80} />);
      const progressFill = container.querySelector('.h-full');

      expect(progressFill).toHaveClass('bg-success');
    });
  });

  describe('Label Display', () => {
    it('should not show label by default', () => {
      render(<ProgressBar progress={50} />);

      expect(screen.queryByText('50% complete')).not.toBeInTheDocument();
    });

    it('should show label when showLabel is true', () => {
      render(<ProgressBar progress={50} showLabel />);

      expect(screen.getByText('50% complete')).toBeInTheDocument();
    });

    it('should show correct label for different progress values', () => {
      const { rerender } = render(<ProgressBar progress={25} showLabel />);
      expect(screen.getByText('25% complete')).toBeInTheDocument();

      rerender(<ProgressBar progress={75} showLabel />);
      expect(screen.getByText('75% complete')).toBeInTheDocument();

      rerender(<ProgressBar progress={100} showLabel />);
      expect(screen.getByText('100% complete')).toBeInTheDocument();
    });

    it('should apply correct label styling', () => {
      render(<ProgressBar progress={50} showLabel />);
      const label = screen.getByText('50% complete');

      expect(label).toHaveClass('text-xs');
      expect(label).toHaveClass('text-gray');
      expect(label).toHaveClass('mt-1');
    });
  });

  describe('Custom ClassName', () => {
    it('should apply custom className to container', () => {
      const { container } = render(
        <ProgressBar progress={50} className="custom-class" />
      );

      expect(container.firstChild).toHaveClass('custom-class');
    });

    it('should apply multiple custom classes', () => {
      const { container } = render(
        <ProgressBar progress={50} className="class1 class2 class3" />
      );

      const wrapper = container.firstChild;
      expect(wrapper).toHaveClass('class1');
      expect(wrapper).toHaveClass('class2');
      expect(wrapper).toHaveClass('class3');
    });
  });

  describe('Transition Classes', () => {
    it('should have transition classes on progress fill', () => {
      const { container } = render(<ProgressBar progress={50} />);
      const progressFill = container.querySelector('.h-full');

      expect(progressFill).toHaveClass('transition-all');
      expect(progressFill).toHaveClass('duration-300');
    });
  });

  describe('Edge Cases', () => {
    it('should handle negative progress (treated as 0)', () => {
      const { container } = render(<ProgressBar progress={-10} />);
      const progressFill = container.querySelector('.h-full');

      expect(progressFill).toHaveStyle({ width: '-10%' }); // Browser will clamp this
    });

    it('should handle progress over 100', () => {
      const { container } = render(<ProgressBar progress={150} />);
      const progressFill = container.querySelector('.h-full');

      expect(progressFill).toHaveStyle({ width: '150%' }); // Browser will clamp this
    });

    it('should handle decimal progress values', () => {
      const { container } = render(<ProgressBar progress={33.33} showLabel />);
      const progressFill = container.querySelector('.h-full');

      expect(progressFill).toHaveStyle({ width: '33.33%' });
      expect(screen.getByText('33.33% complete')).toBeInTheDocument();
    });
  });
});
