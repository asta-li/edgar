import React from 'react';

// Material UI imports.
import CssBaseline from '@material-ui/core/CssBaseline';
import Box from '@material-ui/core/Box';
import Typography from '@material-ui/core/Typography';
import Container from '@material-ui/core/Container';
import {makeStyles} from '@material-ui/styles';

// Local imports.
import logo from './logo.png';
import {DataDisplay} from './DataDisplay.js';
import {QueryInput} from './QueryInput.js';

// Styles the Home component.
const useStyles = makeStyles((theme) => ({
  paper: {
    marginTop: theme.spacing(5),
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  logo: {
    margin: theme.spacing(5),
    width: theme.spacing(14),
    height: theme.spacing(14),
  },
  intro: {
    marginBottom: theme.spacing(5),
  },
  spacing: {
    marginTop: theme.spacing(5),
  },
}));

const Copyright = () => {
  return (
      <Typography variant="body2" color="textSecondary" align="center">
        {'Copyright ©'}
        {' Edgar '}
        {new Date().getFullYear()}
        {'.'}
      </Typography>
  );
}

const App = () => {
  const classes = useStyles();
  const [response, setResponse] = React.useState(null);

  return (
    <div>
      <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap" />
      <CssBaseline />
      <Container className={classes.paper} component="main" maxWidth="md">
          <img className={classes.logo} src={logo} alt="Logo" />
          <Typography component="h1" variant="h4" gutterBottom>
            Hi, I'm Edgar.
          </Typography>
          <Typography className={classes.intro} component="h2" variant="h6" gutterBottom>
            I'm here to help you research your investments.
          </Typography>
          <QueryInput setResponse={setResponse} />
          <Typography className={classes.spacing}></Typography>
          <DataDisplay response={response} />
      </Container>
      <Box mt={50}>
        <Copyright />
      </Box>
      </div>
  );
}

export default App;
