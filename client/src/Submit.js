import axios from 'axios';
import React from 'react';
import PropTypes from 'prop-types';
import Button from '@material-ui/core/Button';
import CssBaseline from '@material-ui/core/CssBaseline';
import Link from '@material-ui/core/Link';
import Box from '@material-ui/core/Box';
import Typography from '@material-ui/core/Typography';
import Container from '@material-ui/core/Container';

import { validateFaxNumber } from './FaxNumberValidation.js'

// Controls faxing a selected file.
class FileFaxer extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      faxFileStatus: '',
    };
    this.handleFileFax = this.handleFileFax.bind(this);
  }

  handleFileFax() {
    let passedValidation = true;

    // Make sure a file has successfully been selected.
    // If the file exists, it has already been validated.
    if (!this.props.selectedFile) {
      const error = 'Select a file to fax.';
      this.props.setSelectedFileError(error);
      passedValidation = false;
    }
    // Validate the input fax number.
    const faxNumberError = validateFaxNumber(this.props.faxNumber);
    if (faxNumberError) {
      this.props.setFaxNumberError(faxNumberError);
      passedValidation = false;
    }

    if (!passedValidation) {
      return;
    }
    
    // All validation stages have passed. Now, send the fax.
    console.log('Faxing', this.props.selectedFile);
    console.log('Destination', this.props.faxNumber);
    this.setState({
      faxFileStatus: 'Faxing...',
    });

    // Create form containing the file data.
    const formData = new FormData();
    formData.append('file', this.props.selectedFile);
    formData.append('faxNumber', this.props.faxNumber);

    const config = {
      headers: { 'content-type': 'multipart/form-data' },
    };

    // Sends the file to the backend for payment processing, upload, and faxing.
    axios.post('/api/upload', formData, config)
      .then((response) => {
        console.log('Received successful fax response', response);

        // window.open(response.data.redirectUrl, '', 'location:no, height=687, width=500')
        window.location.href = response.data.redirectUrl;
        this.setState({
          faxFileStatus: 'Successfully uploaded ' + response.data.FaxId + ' for $' + response.data.Price + '!',
        });
        // let parent know that upload is successful
        this.props.uploadSuccessHandler()
      })
      .catch((error) => {
        console.log(error);
        this.setState({
          faxFileStatus: 'Unable to fax!',
        });
      });
  }

  // Render the element that controls faxing the selected file.
  render() {
    return (
      <React.Fragment>
        <Button
          className={this.props.className}
          fullWidth
          variant="contained"
          color="primary"
          onClick={this.handleFileFax}
        >
          Fax me!
        </Button>
        {this.state.faxFileStatus}
      </React.Fragment>
    );
  }
}

export { FileFaxer };
