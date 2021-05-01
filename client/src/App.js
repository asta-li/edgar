import React from 'react';
import {Link, Route, Switch, useLocation} from 'react-router-dom';
import PropTypes from 'prop-types';

// Material UI imports.
import CssBaseline from '@material-ui/core/CssBaseline';
import MLink from '@material-ui/core/Link';
import Box from '@material-ui/core/Box';
import Typography from '@material-ui/core/Typography';
import Container from '@material-ui/core/Container';
import {makeStyles} from '@material-ui/styles';

// Local imports.
import {FileInput} from './FileInput.js';
import {FaxNumberInput} from './FaxNumberInput.js';
import {FileFaxer} from './Submit.js';
import logo from './logo.png'; 
import SendingFax from "./components/SendingFax";

// Styles the Home component.
const useStyles = makeStyles((theme) => ({
  paper: {
    marginTop: theme.spacing(8),
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  logo: {
    margin: theme.spacing(1),
    width: theme.spacing(10),
    height: theme.spacing(10),
  },
  form: {
    width: '100%',
    marginTop: theme.spacing(1),
  },
  submit: {
    margin: theme.spacing(0, 0, 0),
  },
}));

// A custom hook that builds on useLocation to parse
// the query string for you.
function useQuery() {
  return new URLSearchParams(useLocation().search);
}

function Copyright() {
  return (
      <Typography variant="body2" color="textSecondary" align="center">
        {'Copyright ©'}
        {' Fax Machine Dev '}
        {new Date().getFullYear()}
        {'.'}
      </Typography>
  );
}

const FaxMachineApp = () => {

  let query = useQuery();

  return <Container component="main" maxWidth="xs">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap" />
    <CssBaseline />
    <div>
      {/* A <Switch> looks through its children <Route>s and
            renders the first one that matches the current URL. */}
      <Switch>
        <Route exact path="/">
          <Home action={query.get("action")} transactionId={query.get("transactionId")} token={query.get("token")} payerId={query.get("PayerId")} />
        </Route>

      </Switch>
    </div>
    <Box mt={8}>
      <Copyright />
    </Box>
  </Container>
};


const Home = props => {
  const [selectedFile, setSelectedFile] = React.useState(null);
  const [selectedFileError, setSelectedFileError] = React.useState('');
  const [faxNumber, setFaxNumber] = React.useState('+16504344807');
  const [faxNumberError, setFaxNumberError] = React.useState('');
  const [isUploadSuccess, setUploadSuccess] = React.useState(false);

  const uploadSuccessHandler = (id) => {
    setUploadSuccess(true);
  };

  let showFileFaxer;

  const classes = useStyles();

  if (!isUploadSuccess && !props.action) {
    showFileFaxer =
      <Container className={classes.paper} component="main" maxWidth="s">
        <img className={classes.logo} src={logo} alt="Logo" />
        <Typography component="h1" variant="h4" gutterBottom>
          I am a fax machine.
        </Typography>
        <form className={classes.form} noValidate>
          {/* Controls fax number input. */}
          <FaxNumberInput
            setFaxNumber={setFaxNumber}
            faxNumberError={faxNumberError}
            setFaxNumberError={setFaxNumberError}
          />
          {/* Controls file selection and validation. This component allows a user to select a */}
          {/* file, validates the file, and updates the file information in the app state. */}
          <FileInput
            selectedFile={selectedFile}
            setSelectedFile={setSelectedFile}
            selectedFileError={selectedFileError}
            setSelectedFileError={setSelectedFileError}
          />
          {/* Controls file upload and faxing. */}
          <FileFaxer
            className={classes.submit}
            selectedFile={selectedFile}
            setSelectedFileError={setSelectedFileError}
            faxNumber={faxNumber}
            setFaxNumberError={setFaxNumberError}
            uploadSuccessHandler={uploadSuccessHandler}
          />
        </form>
      </Container>;
  }
  else {
    showFileFaxer = <div></div>;
  }

  return <div>
    <div>
      {showFileFaxer}
      {
        isUploadSuccess ?
            <div>
              file succesfully uploaded!
              you're redirected to paypal for payment!
            </div> :
            <div></div>
      }
    </div>
    <div>
      {
        props.action === "process" ? (
            <div>
              <SendingFax transactionId={props.transactionId}/>
            </div>
        ) : (
            <h3></h3>
        )
      }
    </div>
  </div>
};

export default FaxMachineApp;
