export type ReviewKind =
  | "personal"
  | "recommendation"
  | "first_impression"
  | "long_term"
  | "comparison"
  | "question";

export type ReviewState =
  | "draft"
  | "pending_moderation"
  | "needs_review"
  | "published"
  | "rejected"
  | "archived"
  | "deleted";
