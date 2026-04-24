import { RoleUtilisateur } from '../constantes/roles.const';

export interface Utilisateur {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  matricule: string;
  role: RoleUtilisateur | string;
  email_verified: boolean;
  full_name?: string;
}
