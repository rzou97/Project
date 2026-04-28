import { HttpErrorResponse, HttpInterceptorFn, HttpRequest } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, finalize, map, Observable, shareReplay, switchMap, throwError } from 'rxjs';
import { API_ENDPOINTS } from '../constantes/api.const';
import { ROUTE_PATHS } from '../constantes/routes.const';
import { AuthService } from '../auth/auth.service';
import { SessionService } from '../auth/session.service';

let refreshTokenRequest$: Observable<string> | null = null;

function isAnonymousRequest(url: string): boolean {
  return (
    url === API_ENDPOINTS.connexion ||
    url === API_ENDPOINTS.rafraichirToken ||
    url === API_ENDPOINTS.inscription ||
    url.startsWith(API_ENDPOINTS.activationCompteBase)
  );
}

function withBearerToken<T>(req: HttpRequest<T>, token: string): HttpRequest<T> {
  return req.clone({
    setHeaders: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export const jwtInterceptor: HttpInterceptorFn = (req, next) => {
  const sessionService = inject(SessionService);
  const authService = inject(AuthService);
  const router = inject(Router);

  if (isAnonymousRequest(req.url)) {
    return next(req);
  }

  const token = sessionService.obtenirAccessToken();

  if (token) {
    req = withBearerToken(req, token);
  }

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status !== 401) {
        return throwError(() => error);
      }

      const refreshToken = sessionService.obtenirRefreshToken();
      if (!refreshToken) {
        sessionService.viderSession();
        void router.navigateByUrl(`/${ROUTE_PATHS.connexion}`);
        return throwError(() => error);
      }

      if (!refreshTokenRequest$) {
        refreshTokenRequest$ = authService.rafraichirToken().pipe(
          map((response) => response.access),
          shareReplay(1),
          finalize(() => {
            refreshTokenRequest$ = null;
          })
        );
      }

      return refreshTokenRequest$.pipe(
        switchMap((freshToken) => next(withBearerToken(req, freshToken))),
        catchError((refreshError) => {
          sessionService.viderSession();
          void router.navigateByUrl(`/${ROUTE_PATHS.connexion}`);
          return throwError(() => refreshError);
        })
      );
    })
  );
};
