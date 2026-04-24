export const ROLES = {
  admin: 'ADMIN',
  operateur: 'OPERATEUR',
  technicien: 'TECHNICIEN',
  superviseur: 'SUPERVISEUR',
} as const;

export type RoleUtilisateur = (typeof ROLES)[keyof typeof ROLES];
