import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { axe, toHaveNoViolations } from 'jest-axe';
import { ReviewPage } from '../ReviewPage';

expect.extend(toHaveNoViolations);

describe('ReviewPage', () => {
  it('renders', () => {
    render(
      <MemoryRouter initialEntries={['/review/1']}>
        <ReviewPage />
      </MemoryRouter>
    );
  });

  it('has no a11y violations', async () => {
    const { container } = render(
      <MemoryRouter initialEntries={['/review/1']}>
        <ReviewPage />
      </MemoryRouter>
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});