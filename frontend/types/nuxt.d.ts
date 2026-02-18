import Vue from 'vue'

declare module 'vue/types/vue' {
  interface Vue {
    $t: (key: string) => string
    localePath: (path: string) => string
  }
}

declare module 'vue/types/options' {
  interface ComponentOptions<V extends Vue> {
    $t?: (key: string) => string
    localePath?: (path: string) => string
  }
} 