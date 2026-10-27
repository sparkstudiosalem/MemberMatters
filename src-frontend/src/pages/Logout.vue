<template>
  <q-page class="flex flex-center q-pa-md">
    <q-card class="q-pa-lg text-center logout-card">
      <div class="logo-wrapper q-mb-md">
        <q-img
          fit="contain"
          src="/static/spark-logo.svg"
          style="max-height: 48px"
          class="q-mx-auto"
        />
      </div>

      <div class="text-h6 text-weight-bold text-white q-mb-xs">
        Spark Studio Salem
      </div>

      <q-spinner v-if="spinner && !error" color="warning" size="3em" class="q-my-md" />

      <div v-if="!spinner && !error" class="text-positive text-subtitle1 text-weight-bold q-my-md">
        <q-icon name="mdi-check-circle" size="2em" class="q-mr-xs vertical-middle" />
        <span>{{ $t('logoutPage.logoutSuccess') }}</span>
      </div>

      <div v-if="error" class="text-negative text-subtitle1 text-weight-bold q-my-md">
        <q-icon name="mdi-alert-circle" size="2em" class="q-mr-xs vertical-middle" />
        <span>{{ $t('logoutPage.logoutFailed') }}</span>
      </div>

      <div class="text-grey-5 text-caption q-mt-sm">
        Ending session and signing out of SSO...
      </div>
    </q-card>
  </q-page>
</template>

<script lang="ts">
import { mapMutations } from 'vuex';
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'LogoutPage',
  data() {
    return {
      error: false,
      spinner: true,
    };
  },
  async mounted() {
    try {
      await this.$axios.post('/api/logout/');
    } catch (e: any) {
      // Proceed with SSO logout even if API returned 401 or network error
    } finally {
      this.completeLogout();
    }
  },
  methods: {
    ...mapMutations('profile', ['setLoggedIn', 'resetState']),
    ...mapMutations('auth', ['setAuth']),
    completeLogout() {
      this.resetState();
      this.setAuth({ access: '', refresh: '' });
      this.setLoggedIn(false);
      this.error = false;
      this.spinner = false;
      setTimeout(() => {
        const returnUrl = window.location.origin + '/login?logged_out=true';
        window.location.href = `https://auth.sparkstudiosalem.com/flows/-/default/invalidation/?next=${encodeURIComponent(returnUrl)}`;
      }, 750);
    },
  },
});
</script>

<style scoped>
.logout-card {
  max-width: 440px;
  width: 100%;
  background: #181818 !important;
  border: 1px solid rgba(253, 211, 11, 0.28) !important;
  border-radius: 16px !important;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.75), 0 0 24px rgba(253, 211, 11, 0.08) !important;
}
</style>
