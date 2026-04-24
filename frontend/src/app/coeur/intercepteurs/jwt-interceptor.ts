import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { SessionService } from '../auth/session.service';

export const jwtInterceptor: HttpInterceptorFn = (req, next) => {
  const sessionService = inject(SessionService);
  const token = sessionService.obtenirAccessToken();

  if (token) {
    req = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  return next(req);
};