import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Footer, NOTICES } from "@/components/Footer";
import { ReviewCard } from "@/components/ReviewCard";

describe("Footer", () => {
  it("shows required notices", () => {
    render(<Footer />);
    expect(screen.getByText(NOTICES.general)).toBeInTheDocument();
    expect(screen.getByText(/qualified legal review/i)).toBeInTheDocument();
  });
});

describe("ReviewCard", () => {
  it("links to the review", () => {
    render(
      <ReviewCard
        review={{
          id: "r1",
          title: "Quiet enough for a noisy office",
          body: "Demo",
          overall_rating: 5,
          state: "published",
          author: { username: "demo_reviewer" },
          product: {
            name: "QuietLine",
            brand_name: "Harbor Audio",
            category: { name: "Technology" },
          },
        }}
      />,
    );
    expect(screen.getByText("Quiet enough for a noisy office")).toBeInTheDocument();
    expect(screen.getByRole("link")).toHaveAttribute("href", "/reviews/r1");
  });
});
