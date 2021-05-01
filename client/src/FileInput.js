import React from 'react';

import Paper from '@material-ui/core/Paper';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import FormHelperText from '@material-ui/core/FormHelperText';

import { Document, Page, pdfjs } from "react-pdf";
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.js`;


// Controls selection of a local file.
const FileInput = props => {
  // PDF page state getters and setters.
  const [numPages, setNumPages] = React.useState(null);
  const [pageNumber, setPageNumber] = React.useState(1);

  // Update and validate the selected file.
  let handleFileSelection = event => {
    if (event.target.files.length === 0) {
      return;
    }
    const selectedFile = event.target.files[0];
    const { error : selectedFileError }  = validateFile(selectedFile);
    props.setSelectedFileError(selectedFileError);
    if (selectedFileError) {
      props.setSelectedFile(null);
    } else {
      // Update the state with the selected file only after it passes validation.
      props.setSelectedFile(selectedFile);
    }
  }
 
  // Set the number of pages on loading the document.
  let onDocumentLoadSuccess = ({ numPages }) => {
    setNumPages(numPages);
  }

  // Set file selection status.
  let status = 'Please select a file.';
  let error = false;
  let preview = (<div></div>);
  if (props.selectedFileError) {
    error = true;
    status = props.selectedFileError;
  } else if (props.selectedFile) {
    status = props.selectedFile.name; 
    preview = (
      <FormHelperText>
        Preview: Page {pageNumber} of {numPages}
      </FormHelperText>
    )
  }

  // Render the element that controls file seletion.
  return (
    <React.Fragment>
      <Button variant="contained" component="label" required fullWidth>
        Select PDF
        <input
          type="file"
          accept=".pdf,application/pdf"
          hidden
          onChange={handleFileSelection}
        />
      </Button>
      <FormHelperText error={error}>{status}</FormHelperText>
      <Paper elevation={2} align={'center'}>
        <Document
          file={props.selectedFile}
          onLoadSuccess={onDocumentLoadSuccess}
          noData={''}
          options={{
            cMapUrl: 'cmaps/',
            cMapPacked: true,
          }}
        > 
          <Page pageNumber={pageNumber} scale={0.5}/>
        </Document>
      </Paper>
      {preview}
    </React.Fragment>
  );
}

export { FileInput };


// File validation helper functions.
// ===================================================================

// TODO(asta): Perform additional client-side validation,
// such as checking for JavaScript in the file.
//
// Perform basic file validation. Return true if validation is successful.
function validateFile(file) {
  let error = '';

  if (!file) {
    error = 'Please select a PDF file';
    return { error };
  }

  if (file.type !== 'application/pdf') {
    error = 'Selected file must be a PDF';
    return { error };
  }

  const fileSizeMB = file.size / 1024 / 1024;
  const MAX_SIZE_MB = 5;
  if (fileSizeMB > MAX_SIZE_MB) {
    error = 'Selected file is ' + fileSizeMB + 'MB but max is ' + MAX_SIZE_MB + 'MB';
    return { error };
  }

  return { error };
}

