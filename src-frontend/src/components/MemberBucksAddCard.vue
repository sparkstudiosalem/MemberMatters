<template>
  <div class="q-pa-xs">
    <q-card-section class="q-pb-xs">
      <div class="text-h6 text-weight-bold">Add Card</div>
      <div class="text-caption text-grey-6 q-mb-md">
        Add your card below. We don't store your credit card info other than the last 4 digits and expiry. Our secure payment provider stores your card for us.
      </div>
    </q-card-section>

    <q-card-section>
      <div id="stripe-card-element" class="q-mb-md"></div>

      <div v-if="error" class="text-negative text-caption q-mb-md">
        {{ error }}
      </div>

      <div class="row justify-center q-mt-md">
        <q-btn
          id="save-card-button"
          :loading="loading"
          :disable="loading || !stripeReady"
          color="primary"
          icon="mdi-credit-card"
          label="Save Payment Card"
          class="q-px-lg"
          @click="saveCard"
        />
      </div>
    </q-card-section>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';

export default {
  name: 'MemberBucksAddCard',
  data() {
    return {
      stripe: null,
      card: null,
      loading: false,
      stripeReady: false,
      error: '',
    };
  },
  computed: {
    ...mapGetters('config', ['features', 'keys']),
    stripeKey() {
      return (
        this.keys?.stripePublishableKey ||
        this.features?.stripePublishableKey ||
        ''
      );
    },
  },
  watch: {
    stripeKey: {
      immediate: true,
      handler(key) {
        if (key && !this.card) {
          this.$nextTick(() => {
            this.initStripe();
          });
        }
      },
    },
  },
  mounted() {
    if (this.stripeKey && !this.card) {
      this.$nextTick(() => {
        this.initStripe();
      });
    }
  },
  methods: {
    ...mapActions('profile', ['getProfile']),
    initStripe() {
      if (this.card) return;
      if (window.Stripe) {
        this.mountCardElement();
      } else {
        const script = document.createElement('script');
        script.src = 'https://js.stripe.com/v3/';
        script.onload = () => {
          this.mountCardElement();
        };
        document.head.appendChild(script);
      }
    },
    mountCardElement() {
      if (this.card) return;
      const key = this.stripeKey;
      if (!key) {
        console.warn('Stripe publishable key missing in site configuration.');
        return;
      }

      try {
        const targetEl = document.querySelector('#stripe-card-element');
        if (!targetEl) {
          console.warn('#stripe-card-element container not found in DOM.');
          return;
        }

        this.stripe = window.Stripe(key);
        const elements = this.stripe.elements();

        const style = {
          base: {
            color: '#ffffff',
            fontFamily: 'Inter, Roboto, -apple-system, sans-serif',
            fontSmoothing: 'antialiased',
            fontSize: '16px',
            lineHeight: '24px',
            '::placeholder': {
              color: '#d0d0d0',
            },
            ':-webkit-autofill': {
              color: '#ffffff',
            },
            iconColor: '#FDD30B',
          },
          invalid: {
            color: '#ff6b6b',
            iconColor: '#ff6b6b',
          },
        };

        this.card = elements.create('card', { style, hidePostalCode: true });
        this.card.mount('#stripe-card-element');
        this.card.on('ready', () => {
          this.stripeReady = true;
        });
        this.card.on('change', (event) => {
          this.error = event.error ? event.error.message : '';
        });
      } catch (e) {
        console.error('Error initializing Stripe elements:', e);
      }
    },
    async saveCard() {
      if (!this.stripe || !this.card) return;
      this.loading = true;
      this.error = '';

      const { paymentMethod, error } = await this.stripe.createPaymentMethod({
        type: 'card',
        card: this.card,
      });

      if (error) {
        this.error = error.message;
        this.loading = false;
        return;
      }

      this.$axios
        .post('/api/billing/card/', {
          paymentMethodId: paymentMethod.id,
        })
        .then(async () => {
          await this.getProfile();
          this.$emit('card-saved');
        })
        .catch((err) => {
          this.error =
            err.response?.data?.message || 'Error saving card details.';
        })
        .finally(() => {
          this.loading = false;
        });
    },
  },
};
</script>
