export const state = () => ({
  colorTheme: null,
  dark: false,
  snackbar: {
    color: '',
    text: '',
    timeout: 0,
    visible: false
  },
  modality: {},
  lastErrorAlertTime: 0
})

export const mutations = {
  setTheme(state, theme) {
    state.colorTheme = theme
  },
  setDarkMode(state, value) {
    state.dark = value
  },
  setSnackbar(state, payload) {
    state.snackbar = payload
  },
  setModality(state, payload) {
    state.modality = Object.assign(state.modality, payload)
  },
  setLastErrorAlertTime(state, time) {
    state.lastErrorAlertTime = time
  }
}

export const actions = {
  async nuxtServerInit({ commit, _state }, { app }) {
    const theme = app.$cookies.get('theme')
    if (theme) {
      await commit('setTheme', theme)
    }
    const dark = app.$cookies.get('dark')
    if (dark !== undefined) {
      await commit('setDarkMode', dark === 'true')
    }
  }
} 