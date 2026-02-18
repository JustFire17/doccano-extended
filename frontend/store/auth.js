export const state = () => ({
  username: null,
  id: null,
  isAuthenticated: false,
  isStaff: false,
  is_superuser: false,
})

export const mutations = {
  setUsername(state, username) {
    state.username = username
  },
  setUserId(state, userId) {
    state.id = userId
  },
  clearUsername(state) {
    state.username = null
  },
  setAuthenticated(state, isAuthenticated) {
    state.isAuthenticated = isAuthenticated
  },
  setIsStaff(state, isStaff) {
    state.isStaff = isStaff
  },
  setIsSuperuser(state, is_superuser) {
    state.is_superuser = is_superuser
  }
}

export const getters = {
  isAuthenticated(state) {
    return state.isAuthenticated
  },
  getUsername(state) {
    return state.username
  },
  getUserId(state) {
    return state.id
  },
  isStaff(state) {
    return state.isStaff
  },
  is_superuser(state) {
    return state.is_superuser
  },
  getUser(state) {
    return state.isAuthenticated ? {
      id: state.id,
      username: state.username
    } : null
  }
}

export const actions = {
  async authenticateUser({ commit }, authData) {
    try {
      await this.$repositories.auth.login(authData.username, authData.password)
      commit('setAuthenticated', true)
    } catch (error) {
      throw new Error('The credential is invalid')
    }
  },
  async fetchSocialLink() {
    return await this.$repositories.auth.socialLink()
  },
  async initAuth({ commit }) {
    try {
      const user = await this.$repositories.user.getProfile()
      console.log(user)
      commit('setAuthenticated', true)
      commit('setUsername', user.username)
      commit('setUserId', user.id)
      commit('setIsStaff', user.isStaff)
      commit('setIsSuperuser', user.isSuperuser)
    } catch {
      commit('setAuthenticated', false)
      commit('setIsStaff', false)
      commit('setIsSuperuser', false)
    }
  },
  async logout({ commit }) {
    await this.$repositories.auth.logout()
    commit('setAuthenticated', false)
    commit('setIsStaff', false)
    commit('setIsSuperuser', false)
    commit('clearUsername')
  }
}
