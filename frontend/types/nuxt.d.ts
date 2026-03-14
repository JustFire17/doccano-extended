declare module 'vue/types/vue' {
  interface Vue {
    $t: (key: string) => string
    localePath: (path: string) => string
  }
}

declare module 'vue/types/options' {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  interface ComponentOptions<V extends Vue> {
    $t?: (key: string) => string
    localePath?: (path: string) => string
  }
}
