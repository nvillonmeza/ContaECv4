import createMiddleware from 'next-intl/middleware';
import { locales, defaultLocale } from './i18n-config';

// next-intl middleware for locale detection and routing
// This middleware:
// 1. Detects locale from Accept-Language header or cookies
// 2. Redirects to prefixed routes (/en/dashboard, /pt/dashboard)
// 3. Sets the locale cookie for next-intl to use

export default createMiddleware({
  // A list of all locales that are supported
  locales,

  // Used when no locale segment is found
  defaultLocale,

  // Optional: Locale prefix handling
  // - 'as-needed': Only add prefix when needed (recommended for existing apps)
  // - 'always': Always use prefix
  // - 'never': Never use prefix (manual locale handling)
  localePrefix: 'never',

  // Optional: Pathnames for route matching
  // pathnames: {
  //   '/': '/',
  //   '/dashboard': '/dashboard',
  //   '/companies': '/companies',
  //   // ... other routes
  // },

  // Optional: Debug mode for development
  // debugging: process.env.NODE_ENV === 'development'
});

// Configure which routes should be processed by the middleware
export const config = {
  // Match all internationalized paths
  matcher: [
    // Match all paths except api, _next/static, _next/image, favicon.ico, sitemap.xml, robots.txt
    '/((?!api|_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt).*)',
    // Match root path for locale detection
    '/'
  ]
};