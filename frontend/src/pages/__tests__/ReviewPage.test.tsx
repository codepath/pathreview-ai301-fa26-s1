import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { axe } from 'jest-axe'
import { ReviewPage } from '../ReviewPage'
import type { useReviewStatus } from '../../hooks/useReviewStatus'
import { Review } from '../../types'

type ReviewStatus = ReturnType<typeof useReviewStatus>

const { mockUseReviewStatus, mockGetReview } = vi.hoisted(() => ({
  mockUseReviewStatus: vi.fn<[string], ReviewStatus>(),
  mockGetReview: vi.fn<[string], Promise<Review>>(),
}))

vi.mock('../../hooks/useReviewStatus', () => ({ useReviewStatus: mockUseReviewStatus }))
vi.mock('../../services/api', () => ({ apiClient: { getReview: mockGetReview } }))

const completedReview: Review = {
  id: 'r1',
  profile_id: 'p1',
  status: 'complete',
  overall_score: 0.72,
  sections: [
    {
      section_name: 'Projects',
      content: 'Your projects show solid fundamentals.',
      suggestions: ['Add tests to your main project'],
      confidence: 0.9
    }
  ],
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:05:00Z'
}

const failedReview: Review = {
  ...completedReview,
  status: 'failed',
  overall_score: undefined,
  sections: undefined,
  error_message: 'The review could not be completed.'
}

function renderReviewPage() {
  return render(
    <MemoryRouter initialEntries={['/reviews/r1']}>
      <Routes>
        <Route path="/reviews/:reviewId" element={<ReviewPage />} />
      </Routes>
    </MemoryRouter>
  )
}

// jest-axe disables color-contrast rules under jsdom, so these tests do not check contrast (see #42).
describe('ReviewPage accessibility', () => {
  beforeEach(() => {
    mockUseReviewStatus.mockReset()
    mockGetReview.mockReset()
  })

  it('has no axe violations while the review is loading', async () => {
    mockUseReviewStatus.mockReturnValue({ review: null, isPolling: true, error: null })
    const { container } = renderReviewPage()

    expect(screen.getByText('Analyzing your portfolio...')).toBeInTheDocument()
    expect(await axe(container)).toHaveNoViolations()
  })

  it('has no axe violations when the review has failed', async () => {
    mockUseReviewStatus.mockReturnValue({ review: failedReview, isPolling: false, error: null })
    const { container } = renderReviewPage()

    expect(screen.getByText('Review Failed')).toBeInTheDocument()
    expect(await axe(container)).toHaveNoViolations()
  })

  it('has no axe violations for a completed review', async () => {
    mockUseReviewStatus.mockReturnValue({ review: completedReview, isPolling: false, error: null })
    mockGetReview.mockResolvedValue(completedReview)
    const { container } = renderReviewPage()

    expect(await screen.findByText('Portfolio Review')).toBeInTheDocument()
    expect(await axe(container)).toHaveNoViolations()
  })
})
