<template>
  <div class="q-pa-xs">
    <q-card-section class="q-pb-xs">
      <div class="text-h6 text-weight-bold">
        ACH Bank Transfer Setup
      </div>
      <div class="text-caption text-grey-6 q-mb-xs">
        Enter your US bank account details for direct debit payments with lower processing fees.
      </div>
      <p class="text-caption text-grey-6 q-mb-none">
        * All fields are required.
      </p>
    </q-card-section>

    <q-card-section>
      <q-form @submit.prevent="submitAchForm" class="q-gutter-y-md">
        <q-input
          v-model="form.accountHolderName"
          outlined
          dense
          label="Account Holder Name *"
          :lazy-rules="true"
          :rules="[(val) => (val && val.length > 0) || 'Name is required']"
        >
          <template v-slot:hint>
            <span class="subtext-hint">Full name on bank account</span>
          </template>
        </q-input>

        <div class="row q-col-gutter-sm">
          <div class="col-12 col-sm-6">
            <q-input
              v-model="form.routingNumber"
              outlined
              dense
              mask="#########"
              label="Routing Number *"
              :lazy-rules="true"
              :rules="[
                (val) => (val && val.length === 9) || '9-digit routing required',
              ]"
            >
              <template v-slot:hint>
                <span class="subtext-hint">9-digit ABA routing number</span>
              </template>
            </q-input>
          </div>

          <div class="col-12 col-sm-6">
            <q-input
              v-model="form.accountNumber"
              outlined
              dense
              type="password"
              name="ach_account_number_no_autofill"
              id="ach_account_number"
              autocomplete="off"
              data-lpignore="true"
              data-1p-ignore="true"
              data-bwignore="true"
              data-form-type="other"
              label="Account Number *"
              :lazy-rules="true"
              :rules="[(val) => (val && val.length >= 4) || 'Account number required']"
            >
              <template v-slot:hint>
                <span class="subtext-hint">Bank account number</span>
              </template>
            </q-input>
          </div>
        </div>

        <div class="row q-col-gutter-sm">
          <div class="col-12 col-sm-6">
            <q-select
              v-model="form.accountType"
              outlined
              dense
              :options="accountTypeOptions"
              emit-value
              map-options
              label="Account Type *"
            />
          </div>

          <div class="col-12 col-sm-6">
            <q-select
              v-model="form.accountHolderType"
              outlined
              dense
              :options="holderTypeOptions"
              emit-value
              map-options
              label="Holder Type *"
            />
          </div>
        </div>

        <q-banner v-if="error" class="text-white bg-negative rounded-borders q-my-sm">
          {{ error }}
        </q-banner>

        <div class="row justify-center q-pt-sm">
          <q-btn
            type="submit"
            color="primary"
            :loading="loading"
            :disable="loading"
            label="Save ACH Bank Account"
            icon="mdi-bank"
          />
        </div>
      </q-form>
    </q-card-section>
  </div>
</template>

<script>
import { defineComponent } from 'vue';
import { mapGetters, mapActions } from 'vuex';
import { loadStripe } from '@stripe/stripe-js';
import icons from '@icons';

export default defineComponent({
  name: 'MemberBucksAddAch',
  data() {
    return {
      stripe: null,
      loading: false,
      error: null,
      form: {
        accountHolderName: '',
        routingNumber: '',
        accountNumber: '',
        accountType: 'checking',
        accountHolderType: 'individual',
      },
      accountTypeOptions: [
        { label: 'Checking Account', value: 'checking' },
        { label: 'Savings Account', value: 'savings' },
      ],
      holderTypeOptions: [
        { label: 'Individual', value: 'individual' },
        { label: 'Company / Business', value: 'company' },
      ],
    };
  },
  computed: {
    ...mapGetters('profile', ['profile']),
    ...mapGetters('config', ['keys', 'features']),
    icons() {
      return icons;
    },
  },
  watch: {
    async keys(value) {
      if (!this.stripe && value?.stripePublishableKey) {
        await this.setupStripe(value.stripePublishableKey);
      }
    },
  },
  async mounted() {
    if (this.profile?.fullName) {
      this.form.accountHolderName = this.profile.fullName;
    }
    if (
      !this.stripe &&
      this.features?.enableStripe &&
      this.keys?.stripePublishableKey
    ) {
      await this.setupStripe(this.keys.stripePublishableKey);
    }
  },
  methods: {
    ...mapActions('profile', ['getProfile']),
    async setupStripe(stripePublishableKey) {
      if (stripePublishableKey) {
        this.stripe = await loadStripe(stripePublishableKey);
      }
    },
    async submitAchForm() {
      this.error = null;
      this.loading = true;

      try {
        if (!this.stripe && this.keys?.stripePublishableKey) {
          await this.setupStripe(this.keys.stripePublishableKey);
        }

        if (!this.stripe) {
          throw new Error('Stripe service is currently unavailable.');
        }

        const { paymentMethod, error } = await this.stripe.createPaymentMethod({
          type: 'us_bank_account',
          us_bank_account: {
            account_number: this.form.accountNumber,
            routing_number: this.form.routingNumber,
            account_holder_type: this.form.accountHolderType,
            account_type: this.form.accountType,
          },
          billing_details: {
            name: this.form.accountHolderName || this.profile.fullName,
            email: this.profile.email,
          },
        });

        if (error) {
          this.error = error.message;
          this.loading = false;
          return;
        }

        const response = await this.$axios.post('/api/billing/card/', {
          paymentMethodId: paymentMethod.id,
        });

        if (response.status === 200 || response.data?.success) {
          await this.getProfile();
          this.$emit('saved');
        } else {
          this.error = response.data?.message || 'Failed to save bank account details.';
        }
      } catch (err) {
        this.error =
          err?.response?.data?.message || err?.message || 'An error occurred while saving your bank account.';
      } finally {
        this.loading = false;
      }
    },
  },
});
</script>

<style scoped>
.rounded-borders {
  border-radius: 8px;
}

.subtext-hint {
  color: #9e9e9e !important;
}

:deep(.q-field__hint) {
  color: #9e9e9e !important;
}

:deep(.q-field--error .q-field__messages) {
  color: #f44336 !important;
}
</style>
