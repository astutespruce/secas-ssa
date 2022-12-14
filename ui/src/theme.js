const { darken } = require('@theme-ui/color')

// SECAS Palette:
// Dark blue from Blueprint (high): 08306b
// Light blue from Blueprint (med): 4faeee
// Gray-blue: 708ea6
// Accent/call to action orange: f5933b
// Accent green: 569031

module.exports = {
  breakpoints: ['600px', '800px', '1600px'],
  colors: {
    text: '#333',
    background: '#fff',
    primary: '#4279A6', // gray-blue with more saturation
    link: '#006fbe',
    accent: '#f5933b',
    error: '#D04608',
    ok: '#569031',
    grey: {
      // based on primary
      0: '#f9f9fa',
      1: '#eceeef',
      2: '#dee1e4',
      3: '#cfd3d8',
      4: '#bec5ca',
      5: '#acb4bc',
      6: '#97a1ab',
      7: '#7e8b96',
      8: '#606e7b',
      9: '#384048',
    },
    blue: {
      // based on light blue
      0: '#f5fafe',
      1: '#dff0fc',
      2: '#c7e5fa',
      3: '#acd9f7',
      4: '#8ecbf4',
      5: '#6bbbf1',
      6: '#4ca7e5',
      7: '#4190c5',
      8: '#34719b',
      9: '#1e435b',
    },
  },

  fonts: {
    body: '"Source Sans Pro", sans-serif',
    heading: '"Source Sans Pro", sans-serif',
  },
  fontSizes: [14, 16, 18, 20, 24, 32, 48, 64, 72],
  fontWeights: {
    body: 400,
    heading: 900,
    bold: 700,
  },
  layout: {
    container: {
      maxWidth: '960px',
    },
    sidebar: {
      width: ['100%', '320px', '468px', '600px'],
      borderRightWidth: ['0px', '1px'],
      borderRightColor: 'grey.3',
    },
  },
  text: {
    default: {
      display: 'block', // fix for theme-ui v6 (div => span)
    },
    heading: {
      fontFamily: 'heading',
      fontWeight: 'heading',
      lineHeight: 'heading',
    },
    subheading: {
      fontFamily: 'body',
      fontWeight: 'normal',
    },
  },
  lineHeights: {
    body: 1.4,
    heading: 1.2,
  },
  boxes: {
    step: {
      display: 'flex',
      flex: '0 0 auto',
      color: '#FFF',
      bg: 'grey.9',
      borderRadius: '5em',
      width: '3rem',
      height: '3rem',
      alignItems: 'center',
      justifyContent: 'center',
      fontWeight: 'bold',
      mr: '0.75rem',
      fontSize: '1.5rem',
    },
  },

  buttons: {
    primary: {
      cursor: 'pointer',
    },
    disabled: {
      cursor: 'not-allowed',
      color: 'grey.7',
      bg: 'blue.1',
    },
    secondary: {
      cursor: 'pointer',
      color: 'grey.9',
      bg: 'grey.1',
    },
    close: {
      cursor: 'pointer',
      outline: 'none',
      background: 'none',
      color: 'grey.5',
      '&:hover': { color: 'grey.9' },
    },
    header: {
      cursor: 'pointer',
      border: '1px solid #FFF',
      p: '0.25em 0.5em',
      marginLeft: '1rem',
      '&:hover': {
        bg: darken('primary', 0.05),
      },
    },
  },
  forms: {
    input: {
      outline: 'none',
      border: '1px solid',
      borderColor: 'grey.3',
      borderRadius: '0.25rem',
      py: '0.25rem',
      px: '0.5rem',
      '&:active,&:focus': {
        borderColor: 'primary',
      },
    },
    textarea: {
      fontFamily: 'body',
      fontSize: 1,
      lineHeight: 1.3,
      outline: 'none',
      border: '1px solid',
      borderColor: 'grey.3',
      borderRadius: '0.25rem',
      py: '0.25rem',
      px: '0.5rem',
      '&:active,&:focus': {
        borderColor: 'primary',
      },
    },
  },
  modal: {
    background: 'grey.9',
  },
  styles: {
    root: {
      height: '100%',
      overflowX: 'hidden',
      overflowY: 'hidden',
      margin: 0,
      body: {
        margin: 0,
        height: '100%',
        width: '100%',
      },
      '#___gatsby': {
        height: '100%',
      },
      '#___gatsby > *': {
        height: '100%',
      },
      fontFamily: 'body',
      fontWeight: 'body',
      lineHeight: 'body',
      a: {
        color: 'link',
        textDecoration: 'none',
        '&:visited': 'link',
        '&:hover': {
          textDecoration: 'underline',
        },
      },
      p: {
        fontSize: 2,
        color: 'grey.9',
      },
      ul: {
        margin: 0,
        padding: '0 0 0 1rem',
        color: 'grey.9',
        fontSize: 1,
        '& li + li': {
          mt: '0.5rem',
        },
      },
      h1: {
        variant: 'text.heading',
        fontSize: [5, 6, 7],
        color: 'grey.9',
      },
      h2: {
        variant: 'text.heading',
        fontSize: [4, 5],
        color: 'grey.9',
      },
      h3: {
        variant: 'text.heading',
        fontSize: [3, 4],
        color: 'grey.9',
      },
      h4: {
        fontSize: [2, 3],
        variant: 'text.subheading',
        color: 'grey.9',
      },
    },
    hr: {
      color: 'blue.9',
      borderBottom: '0.5rem solid',
      my: '2rem',
    },
    progress: {
      color: 'primary',
      bg: 'grey.1',
      height: '1rem',
      percent: {
        color: 'primary',
        bg: 'grey.2',
        height: '0.75rem',
      },
    },
  },
}
