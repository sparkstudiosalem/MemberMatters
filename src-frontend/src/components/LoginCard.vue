<template>
  <div class="q-pa-md login-card-container flex flex-center">
    <div class="text-center q-pa-lg login-redirect-card">
      <div class="logo-wrapper q-mb-md">
        <q-img
          v-if="images.siteLogo"
          fit="contain"
          :src="images.siteLogo"
          style="max-height: 48px; cursor: pointer"
          class="q-mx-auto"
        />
        <q-img
          v-else
          fit="contain"
          src="/static/spark-logo.svg"
          style="max-height: 48px; cursor: pointer"
          class="q-mx-auto"
        />
      </div>

      <div class="text-h5 text-weight-bolder text-white tracking-wide q-mb-xs">
        Spark Studio Salem
      </div>
      <div class="text-subtitle2 text-grey-5 q-mb-lg">
        Makerspace & Member Portal
      </div>

      <template v-if="isLoggedOut">
        <div class="text-subtitle1 text-weight-bold text-white q-mb-xs">
          Signed Out
        </div>
        <div class="text-caption text-grey-4 q-mb-lg">
          You have been successfully signed out of your account.
        </div>
        <div>
          <q-btn
            unelevated
            no-caps
            class="full-width q-py-sm text-weight-bold"
            style="background: #FDD30B; color: #121212; border-radius: 8px; font-size: 1rem;"
            label="Sign In"
            @click="loginWithSSO"
          />
        </div>
      </template>

      <template v-else>
        <q-circular-progress
          indeterminate
          size="44px"
          :thickness="0.2"
          color="warning"
          track-color="grey-9"
          class="q-mb-md"
        />

        <div class="text-caption text-grey-4 q-mb-md">
          Redirecting to Spark Studio Sign-In...
        </div>

        <div>
          <q-btn
            flat
            dense
            no-caps
            size="sm"
            color="warning"
            label="Click here if you are not redirected automatically"
            @click="loginWithSSO"
          />
        </div>
      </template>
    </div>
  </div>
</template>

<script lang="ts">
import { mapMutations, mapGetters, mapActions } from 'vuex';
import formMixin from '../mixins/formMixin';
import { SplashScreen } from '@capacitor/splash-screen';
import { defineComponent } from 'vue';
import icons from '../icons';

export default defineComponent({
  name: 'LoginCard',
  mixins: [formMixin],
  props: {
    resetToken: {
      type: String,
      default: null,
    },
    noRedirect: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      redirecting: false,
    };
  },
  async mounted() {
    // check if we're logged in and our session is still valid
    await this.retrieveAuth();
    await this.getLoggedIn();

    if (this.loggedIn) {
      this.redirectLoggedIn(false);
    } else {
      await SplashScreen.hide();
      if (!this.isLoggedOut) {
        this.loginWithSSO();
      }
    }
  },
  methods: {
    ...mapActions('profile', ['getLoggedIn']),
    ...mapActions('auth', ['retrieveAuth']),
    ...mapMutations('profile', ['setLoggedIn']),
    ...mapMutations('auth', ['setAuth']),
    /**
     * Redirects to the dashboard page on successful login.
     */
    redirectLoggedIn(delay = true) {
      this.$emit('login-complete');

      if (this.$route.query.next) {
        window.location.replace(this.$route.query.next as string);
        return;
      }

      if (this.$route.query.nextUrl) {
        this.setLoggedIn(true);
        this.$router.push(this.$route.query.nextUrl as string);
      } else if (!this.noRedirect && delay) {
        setTimeout(() => {
          this.setLoggedIn(true);
          this.$router.push({ name: 'dashboard' });
          setTimeout(SplashScreen.hide, 500);
        }, 1000);
      } else {
        this.$router.push({ name: 'dashboard' });
        setTimeout(SplashScreen.hide, 500);
      }
    },
    loginWithSSO() {
      if (this.redirecting) return;
      this.redirecting = true;
      const nextUrl = (this.$route.query.next || this.$route.query.nextUrl || '/dashboard') as string;
      window.location.href = `/api/auth/authentik/login/?next=${encodeURIComponent(nextUrl)}`;
    },
  },
  computed: {
    ...mapGetters('profile', ['loggedIn']),
    ...mapGetters('config', ['siteName', 'images', 'features']),
    icons() {
      return icons;
    },
    isLoggedOut() {
      return Boolean(this.$route.query.logged_out);
    },
  },
});
</script>

<style scoped>
.login-card-container {
  width: 100%;
}

.login-redirect-card {
  max-width: 440px;
  width: 100%;
  background: #181818 !important;
  border: 1px solid rgba(253, 211, 11, 0.28) !important;
  border-radius: 16px !important;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.75), 0 0 24px rgba(253, 211, 11, 0.08) !important;
}

.tracking-wide {
  letter-spacing: 0.03em;
}
</style>
