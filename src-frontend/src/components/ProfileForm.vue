<template>
  <div class="profile-form">
    <q-form ref="formRef">
      <q-input
        v-model="form.email"
        outlined
        no-error-icon
        readonly
        :label="$t('form.email')"
        hint="To change your email address, update it in your Authentik Account Settings."
      >
        <template v-slot:append>
          <q-btn
            flat
            dense
            round
            icon="mdi-open-in-new"
            color="primary"
            type="a"
            href="https://auth.sparkstudiosalem.com/if/user/#/settings;page-user-settings"
            target="_blank"
          >
            <q-tooltip>Manage account in Authentik</q-tooltip>
          </q-btn>
        </template>
      </q-input>

      <q-input
        v-model="form.fullName"
        outlined
        no-error-icon
        :debounce="debounceLength"
        label="Full name *"
        :rules="[
          (val) => validateNotEmpty(val) || $t('validation.cannotBeEmpty'),
        ]"
        @update:model-value="saveFullName"
      >
        <template v-slot:append>
          <saved-notification
            :success="saved.fullName"
            show-text
            :error="saved.error"
          />
        </template>
      </q-input>

      <q-input
        v-model="form.screenName"
        outlined
        no-error-icon
        :debounce="debounceLength"
        :label="$t('form.screenName')"
        :rules="[
          (val) => validateNotEmpty(val) || $t('validation.cannotBeEmpty'),
        ]"
        @update:model-value="saveChange('screenName')"
      >
        <template v-slot:append>
          <saved-notification
            :success="saved.screenName"
            show-text
            :error="saved.error"
          />
        </template>
      </q-input>

      <q-input
        v-model="form.phone"
        outlined
        no-error-icon
        :debounce="debounceLength"
        :label="$t('form.mobile')"
        :rules="[
          (val) => validateNotEmpty(val) || $t('validation.invalidPhone'),
        ]"
        @update:model-value="saveChange('phone')"
      >
        <template v-slot:append>
          <saved-notification
            :success="saved.phone"
            show-text
            :error="saved.error"
          />
        </template>
      </q-input>

      <q-input
        v-if="features?.signup?.collectVehicleRegistrationPlate"
        v-model="form.vehicleRegistrationPlate"
        outlined
        no-error-icon
        :debounce="debounceLength"
        :label="$t('form.vehicleRegistrationPlate')"
        :rules="[(val) => validateMax30(val) || $t('validation.max30')]"
        @update:model-value="saveChange('vehicleRegistrationPlate')"
      >
        <template v-slot:append>
          <saved-notification
            :success="saved.vehicleRegistrationPlate"
            show-text
            :error="saved.error"
          />
        </template>
      </q-input>
    </q-form>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';
import icons from '../icons';
import formMixin from '../mixins/formMixin';
import SavedNotification from '@components/SavedNotification.vue';

export default {
  name: 'ProfileForm',
  components: {
    SavedNotification,
  },
  mixins: [formMixin],
  data() {
    return {
      form: {
        email: '',
        fullName: '',
        firstName: '',
        lastName: '',
        phone: '',
        screenName: '',
        vehicleRegistrationPlate: '',
      },
      saved: {
        // if there was an error saving the form
        error: false,

        email: false,
        fullName: false,
        firstName: false,
        lastName: false,
        phone: false,
        screenName: false,
        vehicleRegistrationPlate: false,
      },
    };
  },
  methods: {
    ...mapActions('profile', ['getProfile']),
    loadInitialForm() {
      this.form.email = this.profile.email;
      this.form.fullName = (this.profile.firstName || '').trim();
      this.form.firstName = (this.profile.firstName || '').trim();
      this.form.lastName = '';
      this.form.phone = this.profile.phone;
      this.form.screenName = this.profile.screenName;
      this.form.vehicleRegistrationPlate =
        this.profile.vehicleRegistrationPlate;
    },
    saveFullName() {
      this.form.firstName = (this.form.fullName || '').trim();
      this.form.lastName = '';
      this.saveChange('fullName');
    },
    saveChange(field) {
      this.$refs.formRef.validate(false).then(() => {
        this.$refs.formRef.validate(false).then((result) => {
          if (result) {
            this.$axios
              .put('/api/profile/', this.form)
              .then(() => {
                this.saved.error = false;
                this.saved[field] = true;
                setTimeout(() => {
                  this.saved[field] = false;
                }, 1500);
                this.getProfile();
              })
              .catch(() => {
                this.saved.error = true;
                this.saved[field] = true;
                setTimeout(() => {
                  this.saved[field] = false;
                  this.saved.error = false;
                }, 1500);
              });
          }
        });
      });
    },
  },
  watch: {
    profile() {
      this.loadInitialForm();
    },
  },
  beforeMount() {
    this.loadInitialForm();
  },
  computed: {
    ...mapGetters('profile', ['profile']),
    ...mapGetters('config', ['features']),
    icons() {
      return icons;
    },
  },
};
</script>

<style lang="sass">
.profile-form
  max-width: $maxWidthMedium
  width: 100%
</style>
