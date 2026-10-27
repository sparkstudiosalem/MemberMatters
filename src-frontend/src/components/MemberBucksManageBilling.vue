<template>
  <q-card :flat="flat" class="billing-card shadow-1">
    <template v-if="this.features.enableStripe">
      <template v-if="cardExists">
        <q-card-section>
          <div class="text-h6">
            {{ isAchSaved ? 'Saved ACH Bank Account' : $t('memberbucks.savedCardTitle') }}
          </div>
          <div class="text-subtitle2 text-grey-7">
            {{
              isAchSaved
                ? 'Your active ACH direct debit details for membership billing.'
                : $t('memberbucks.savedCardDescription')
            }}
          </div>
        </q-card-section>

        <q-card-section class="column items-center">
          <template v-if="isAchSaved">
            <q-card flat bordered class="ach-summary-card full-width q-pa-md bg-grey-1 text-grey-9">
              <div class="row items-center justify-between">
                <div class="row items-center">
                  <q-avatar color="primary" text-color="white" icon="mdi-bank" class="q-mr-md" />
                  <div>
                    <div class="text-subtitle1 text-weight-bold">
                      {{ savedBankName || 'Bank Account' }} (ACH)
                    </div>
                    <div class="text-caption text-grey-7">
                      Account ending in •••• {{ savedLast4 }}
                    </div>
                  </div>
                </div>
                <q-chip color="positive" text-color="white" icon="mdi-check-circle" size="sm">
                  Active
                </q-chip>
              </div>
            </q-card>
          </template>

          <template v-else>
            <credit-card
              :name="profile.fullName"
              :expiry="profile.financial.memberBucks.savedCard.expiry"
              :last4="profile.financial.memberBucks.savedCard.last4"
              :brand="profile.financial.memberBucks.savedCard.brand"
              class="shadow-7"
            />
          </template>

          <div class="row q-pt-lg full-width justify-center">
            <q-btn
              id="card-button"
              :loading="removeLoading"
              :disable="removeLoading"
              color="negative"
              outline
              icon="mdi-delete"
              @click="removeCard"
            >
              {{ isAchSaved ? 'Remove Bank Account' : $t('memberbucks.removeCard') }}
            </q-btn>
          </div>
        </q-card-section>
      </template>

      <template v-else>
        <q-card-section class="q-pb-none">
          <div class="text-h6 text-center q-mb-xs">Select Billing Method</div>
          <div class="text-caption text-center text-grey-7 q-mb-md">
            Choose your preferred billing method below.
          </div>

          <div class="row q-col-gutter-md justify-center">
            <div class="col-12 col-sm-6">
              <q-card
                clickable
                v-ripple
                :class="[
                  'method-selection-btn text-center q-pa-md cursor-pointer transition-generic',
                  selectedMethod === 'ach' ? 'active-method border-primary bg-blue-1' : 'bg-grey-1'
                ]"
                @click="selectedMethod = 'ach'"
              >
                <q-badge color="positive" floating label="Preferred - Lower Fees" class="q-pa-xs" />
                <q-icon name="mdi-bank" size="2.5rem" :color="selectedMethod === 'ach' ? 'primary' : 'grey-7'" />
                <div class="text-subtitle1 text-weight-bold q-mt-sm" :class="selectedMethod === 'ach' ? 'text-primary' : ''">
                  ACH Transfer
                </div>
                <div class="text-caption text-grey-7">
                  Direct Bank Debit (Lower processing fees for makerspace)
                </div>
              </q-card>
            </div>

            <div class="col-12 col-sm-6">
              <q-card
                clickable
                v-ripple
                :class="[
                  'method-selection-btn text-center q-pa-md cursor-pointer transition-generic',
                  selectedMethod === 'card' ? 'active-method border-primary bg-blue-1' : 'bg-grey-1'
                ]"
                @click="selectedMethod = 'card'"
              >
                <q-icon name="mdi-credit-card" size="2.5rem" :color="selectedMethod === 'card' ? 'primary' : 'grey-7'" />
                <div class="text-subtitle1 text-weight-bold q-mt-sm" :class="selectedMethod === 'card' ? 'text-primary' : ''">
                  Credit / Debit Card
                </div>
                <div class="text-caption text-grey-7">
                  Instant card setup (Higher processing fees)
                </div>
              </q-card>
            </div>
          </div>
        </q-card-section>

        <q-card-section class="q-pt-md">
          <div v-if="selectedMethod === 'ach'">
            <member-bucks-add-ach @saved="onPaymentMethodSaved" />
          </div>

          <div v-if="selectedMethod === 'card'">
            <member-bucks-add-card />
          </div>
        </q-card-section>
      </template>
    </template>

    <template v-else>
      <q-card-section>
        <div class="text-h6">
          {{ $t('menuLink.billing') }}
        </div>
        <div class="text-subtitle2">
          {{ $t('error.stripeNotConfiguredFeature') }}
        </div>
      </q-card-section>
    </template>
  </q-card>
</template>

<script>
import CreditCard from '@components/CreditCard.vue';
import { mapGetters, mapActions } from 'vuex';
import MemberBucksAddCard from '@components/MemberBucksAddCard.vue';
import MemberBucksAddAch from './MemberBucksAddAch.vue';
import icons from '@icons';

export default {
  name: 'MemberBucksManageBilling',
  components: { MemberBucksAddCard, MemberBucksAddAch, CreditCard },
  props: {
    flat: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  data() {
    return {
      removeLoading: false,
      selectedMethod: 'ach',
    };
  },
  methods: {
    ...mapActions('profile', ['getProfile']),
    async removeCard() {
      this.removeLoading = true;
      this.$axios
        .delete('/api/billing/card/')
        .then(async () => {
          await this.getProfile();
        })
        .catch(() => {
          this.error = this.$t('memberbucks.removeCardError');
        })
        .finally(() => {
          this.removeLoading = false;
        });
    },
    async onPaymentMethodSaved() {
      await this.getProfile();
      this.$emit('card-exists', true);
    },
  },
  mounted() {
    this.$emit('card-exists', this.cardExists);
  },
  watch: {
    cardExists() {
      this.$emit('card-exists', this.cardExists);
    },
  },
  computed: {
    ...mapGetters('profile', ['profile']),
    ...mapGetters('config', ['features']),
    icons() {
      return icons;
    },
    cardExists() {
      return !!this?.profile?.financial?.memberBucks?.savedCard?.last4;
    },
    savedCardInfo() {
      return this?.profile?.financial?.memberBucks?.savedCard;
    },
    isAchSaved() {
      return (
        this.savedCardInfo?.type === 'us_bank_account' ||
        this.savedCardInfo?.expiry === 'ACH' ||
        (!this.savedCardInfo?.expiry && !!this.savedCardInfo?.last4)
      );
    },
    savedBankName() {
      return this.savedCardInfo?.bankName || 'US Bank';
    },
    savedLast4() {
      return this.savedCardInfo?.last4 || '••••';
    },
  },
};
</script>

<style scoped>
.billing-card {
  width: 100%;
}

.method-selection-btn {
  border: 2px solid transparent;
  border-radius: 12px;
  transition: all 0.25s ease-in-out;
}

.method-selection-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.active-method {
  border-color: var(--q-primary, #1976d2) !important;
  box-shadow: 0 4px 12px rgba(25, 118, 210, 0.15) !important;
}

.ach-summary-card {
  border-radius: 10px;
  border: 1px solid #e0e0e0;
}
</style>
