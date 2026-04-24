import { Utilisateur } from './utilisateur.model';

export interface AuthentificationPayload {
  email: string;
  password: string;
}

export interface AuthentificationReponse {
  access: string;
  refresh: string;
  user: Utilisateur;
}

export interface InscriptionPayload {
  first_name: string;
  last_name: string;
  email: string;
  matricule: string;
  role: string;
  password: string;
  confirm_password: string;
}

export interface InscriptionReponse {
  message: string;
  user_id: number;
  email: string;
}

export interface ActivationReponse {
  message: string;
}
