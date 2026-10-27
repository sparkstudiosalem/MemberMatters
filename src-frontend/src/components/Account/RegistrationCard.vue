<template>
  <div class="q-pa-md">
    <q-card class="register-card">
      <q-img
        v-if="images.siteLogo"
        fit="contain"
        :src="images.siteLogo"
        style="max-height: 40px; cursor: pointer"
        class="q-mt-md"
      />

      <h6 class="q-ma-none q-pt-md q-px-md">
        {{ $t('registrationCard.register') }}
      </h6>

      <q-card-section>
        <p class="q-pb-md">
          {{ $t('form.allFieldsRequired') }}
        </p>

        <q-form @submit="onSubmit" @reset="onReset">
          <div class="row q-pb-sm q-col-gutter-sm">
            <q-input
              v-model="form.email"
              class="col-12"
              autofocus
              filled
              no-error-icon
              type="email"
              :label="$t('form.email')"
              lazy-rules
              :rules="[
                (val) => validateEmail(val) || $t('validation.invalidEmail'),
              ]"
            >
              <template v-slot:prepend>
                <q-icon :name="icons.email" />
              </template>
            </q-input>

            <q-input
              v-model="form.fullName"
              class="col-12"
              filled
              no-error-icon
              label="Full name"
              lazy-rules
              :rules="[
                (val) =>
                  validateNotEmpty(val) || $t('validation.cannotBeEmpty'),
              ]"
            >
              <template v-slot:prepend>
                <q-icon :name="icons.profile" />
              </template>
            </q-input>

            <q-input
              v-model="form.screenName"
              class="col-12"
              filled
              no-error-icon
              :label="$t('form.screenName')"
              lazy-rules
              :rules="[
                (val) =>
                  validateNotEmpty(val) || $t('validation.cannotBeEmpty'),
              ]"
            >
              <template v-slot:prepend>
                <q-icon :name="icons.membership" />
              </template>
            </q-input>

            <q-input
              v-model="form.mobile"
              class="col-12"
              filled
              no-error-icon
              type="tel"
              :label="$t('form.mobile')"
              lazy-rules
              :rules="[
                (val) =>
                  validateNotEmpty(val) || $t('validation.cannotBeEmpty'),
              ]"
            >
              <template v-slot:prepend>
                <q-icon :name="icons.phone" />
              </template>
            </q-input>

            <q-input
              v-if="features?.signup?.collectVehicleRegistrationPlate"
              class="col-12 q-mb-lg"
              v-model="form.vehicleRegistrationPlate"
              :label="$t('form.vehicleRegistrationPlate')"
              :hint="$t('form.vehicleRegistrationNote')"
              filled
              no-error-icon
              type="text"
              lazy-rules
              :rules="[(val) => validateMax30(val) || $t('validation.max30')]"
            ></q-input>

            <q-input
              class="col-12"
              v-model="form.password"
              :label="$t('form.password')"
              filled
              no-error-icon
              :type="isPwd ? 'password' : 'text'"
              lazy-rules
              :rules="[
                (val) =>
                  validateNotEmpty(val) || $t('validation.invalidPassword'),
              ]"
            >
              <template v-slot:prepend>
                <q-icon :name="icons.lock" />
              </template>
              <template v-slot:append>
                <q-icon
                  :name="isPwd ? icons.visibilityOff : icons.visibility"
                  class="cursor-pointer"
                  @click="isPwd = !isPwd"
                />
              </template>
            </q-input>
          </div>

          <q-banner v-if="error" class="bg-negative text-white">
            {{ $t('error.requestFailed') }}
          </q-banner>

          <q-banner v-if="errorExists" class="bg-negative text-white">
            {{ $t(errorExists as string) }}
          </q-banner>

          <p class="text-caption">
            {{ $t('registrationCard.alreadyAMember') }}
            <router-link
              :to="{ name: 'login' }"
              :class="$q.dark.isActive ? 'text-white' : 'text-black'"
            >
              {{ $t('registrationCard.loginHere') }}
            </router-link>
          </p>

          <div class="row">
            <q-space />
            <q-btn
              :label="$t('button.submit')"
              type="submit"
              color="primary-btn"
              :loading="buttonLoading"
              :disable="buttonLoading"
            />
          </div>
        </q-form>
      </q-card-section>
    </q-card>
  </div>
</template>

<script lang="ts">
import { mapGetters } from 'vuex';
import formMixin from '../../mixins/formMixin';
import icons from '../../icons';
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'RegistrationCard',
  mixins: [formMixin],
  data() {
    return {
      failed: false,
      error: false,
      errorExists: false as boolean | string,
      complete: false,
      buttonLoading: false,
      isPwd: true,
      form: {
        fullName: '',
        email: null,
        screenName: null,
        mobile: null,
        password: null,
        vehicleRegistrationPlate: null,
      },
    };
  },
  mounted() {
    if (this.loggedIn) this.$router.push({ name: 'dashboard' });
  },
  computed: {
    ...mapGetters('profile', ['loggedIn']),
    ...mapGetters('config', ['features', 'images']),
    icons() {
      return icons;
    },
  },
  methods: {
    onReset() {
      this.form.email = null;
      this.form.password = null;
    },
    onSubmit() {
      this.register();
    },
    /**
     * This sends the registration API request to register the user.
     */
    register() {
      this.errorExists = false;
      this.error = false;
      this.buttonLoading = true;

      // Send single Full Name directly in single backing database field (firstName)
      const fullName = (this.form.fullName || '').trim();

      this.$axios
        .post('/api/register/', {
          firstName: fullName,
          lastName: '',
          email: this.form.email,
          screenName: this.form.screenName,
          mobile: this.form.mobile,
          password: this.form.password,
          vehicleRegistrationPlate: this.form.vehicleRegistrationPlate,
        })
        .then(() => {
          this.failed = false;
          this.error = false;
          this.complete = true;

          this.$router.push({ name: 'registerSuccess' });
        })
        .catch((error) => {
          if (error.response.status === 409) {
            this.errorExists = error.response.data.message;
            this.error = false;
          } else {
            this.error = true;
            this.errorExists = false;
          }
        })
        .finally(() => {
          this.buttonLoading = false;
        });
    },
  },
});
</script>

<style scoped>
.register-card {
  width: 100%;
  max-width: 500px;
}
</style>
