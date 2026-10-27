<template>
  <div class="q-pa-md error-404-page flex flex-center full-height full-width" style="min-height: 80vh">
    <q-card class="error-404-card text-center q-pa-lg">
      <q-img
        v-if="images.siteLogo"
        fit="contain"
        :src="images.siteLogo"
        style="max-height: 40px; cursor: pointer"
        class="q-mt-xs q-mb-sm"
      />

      <div class="q-py-sm">
        <sad-face style="font-size: 2.8rem; color: #FDD30B" />
      </div>

      <h6 class="q-ma-none q-pb-xs text-weight-bold" style="color: #ffffff">
        Page Not Found
      </h6>

      <p class="text-body2 q-mb-lg" style="color: #b0b0b0">
        {{ $t('error.404') }}
      </p>

      <q-card-actions align="center" class="q-pa-none">
        <q-btn
          :to="{ name: 'dashboard' }"
          label="Go Home"
          class="q-px-lg"
        />
      </q-card-actions>
    </q-card>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
import SadFace from '@components/SadFace.vue';

export default {
  name: 'Error-404',
  components: { SadFace },
  computed: {
    ...mapGetters('config', ['images']),
  },
};
</script>

<style scoped>
.error-404-card {
  max-width: 440px;
  width: 100%;
}
</style>
