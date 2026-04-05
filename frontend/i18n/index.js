export default {
  locales: [
    {
      name: 'English',
      code: 'en',
      iso: 'en-CA',
      file: 'en'
    },
    {
      name: '中文',
      code: 'zh',
      iso: 'zh-CN',
      file: 'zh'
    },
    {
      name: 'Français',
      code: 'fr',
      iso: 'fr-CA',
      file: 'fr'
    },
    {
      name: 'Deutsch',
      code: 'de',
      iso: 'de-DE',
      file: 'de'
    }
  ],
  lazy: true,
  langDir: 'i18n/',
  defaultLocale: 'en',
  vueI18n: {
    fallbackLocale: 'en',
    silentTranslationWarn: true,
    silentFallbackWarn: true,
    messages: {
      en: {
        common: {
          showMore: 'Show More',
          showLess: 'Show Less',
          cancel: 'Cancel',
          create: 'Create',
          confirm: 'Confirm',
          close: 'Close'
        },
        projectRules: {
          title: 'Project Rules',
          create: 'Create Rule',
          name: 'Rule Name',
          description: 'Description',
          votingEndDate: 'Voting End Date',
          votingEndTime: 'Voting End Time',
          closeVote: 'Close Vote',
          reopenVote: 'Reopen Vote',
          confirmVote: 'Confirm Vote',
          voteConfirmation: 'Are you sure you want to submit your vote?',
          closeVoteConfirmation: 'Are you sure you want to close this vote?',
          reopenVoteConfirmation: 'Are you sure you want to reopen this vote?',
          votePercentage: 'Vote Percentage',
          vote: 'Vote'
        }
      }
    }
  },
  detectBrowserLanguage: {
    useCookie: true,
    cookieKey: 'i18n_redirected',
    onlyOnRoot: true // for SEO purposes
  }
}
