import { boot } from 'quasar/wrappers';
import { Dialog } from 'quasar';
import i18n from 'src/i18n';

export default boot(({ router, store }) => {
  router.beforeEach(async (to, from, next) => {
    // Ensure auth state & profile are initialized
    let loggedIn = store.getters['profile/loggedIn'];
    if (!loggedIn) {
      try {
        await store.dispatch('auth/retrieveAuth');
        await store.dispatch('profile/getLoggedIn');
        loggedIn = store.getters['profile/loggedIn'];
      } catch (e) {
        // Ignore auth retrieval errors on public routes
      }
    }

    const profile = store.getters['profile/profile'] || {};

    // Check if current user has administrative / staff privileges
    const isStaffOrAdmin = Boolean(
      profile?.permissions?.isStaff ||
        profile?.permissions?.isSuperuser ||
        profile?.isStaff ||
        profile?.isSuperuser ||
        profile?.is_staff ||
        profile?.is_superuser
    );

    // 1. Require Authentication Guard - Auto-direct directly to SSO
    if (to.matched.some((record) => record.meta?.requiresAuth) && !loggedIn) {
      window.location.href = `/api/auth/authentik/login/?next=${encodeURIComponent(to.fullPath || '/dashboard')}`;
      return;
    }

    // 2. Require Admin / Staff Guard
    if (to.matched.some((record) => record.meta?.requiresAdmin) && !isStaffOrAdmin) {
      Dialog.create({
        title: i18n.global.t('error.error'),
        message: i18n.global.t('error.403'),
      });
      return next({ name: 'dashboard' });
    }

    // 3. Require Active Member Guard
    if (to.matched.some((record) => record.meta?.requiresActiveMember)) {
      // Bypass active membership requirement for Admin / Staff users
      if (isStaffOrAdmin) {
        return next();
      }

      // Enforce active membership check for standard non-admin users
      const memberStatus = (
        profile?.memberStatus ||
        profile?.state ||
        ''
      ).toLowerCase();

      const isActiveMember =
        memberStatus === 'active' ||
        memberStatus === 'financial' ||
        profile?.isMember === true;

      if (!isActiveMember) {
        Dialog.create({
          title: i18n.global.t('error.error'),
          message: i18n.global.t('error.403MemberOnly'),
        });
        return next({ name: 'Error403MemberOnly' });
      }
    }

    return next();
  });
});
