export type UserRole = "client" | "freelancer" | "admin";

export type AuthUser = {
  id: string;
  email: string;
  role: UserRole;
};

export type AuthSession = {
  accessToken: string;
  user: AuthUser;
};
