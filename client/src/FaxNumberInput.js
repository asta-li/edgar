import React from 'react';
import { forwardRef } from 'react';

import TextField from '@material-ui/core/TextField';
import { makeStyles } from '@material-ui/core/styles';

import 'react-phone-number-input/style.css';
import PhoneInput from 'react-phone-number-input';

import { validateFaxNumberInProgress } from './FaxNumberValidation.js'


const MuiFaxInput = forwardRef((props, ref) => {
  const faxNumberError = props.children;
  return (
    <TextField
      {...props}
      inputRef={ref}
      fullWidth
      size="small"
      label="Fax Number"
      variant="outlined"
      name="fax-number"
      margin="normal"
      required
      id="fax-number"
      autoComplete="fax-number"
      autoFocus
      error={faxNumberError !== ''}
      helperText={faxNumberError}
    />
  );
});

const FaxNumberInput = props => {
  const onChange = (faxNumber) => {
    const faxNumberError = validateFaxNumberInProgress(faxNumber);
    props.setFaxNumberError(faxNumberError)
    if (!faxNumberError) {
        props.setFaxNumber(faxNumber)
    }
  };
  return (
    <div>
      <PhoneInput
        country={'US'}
        countries={['US']}
        addInternationalOption={false}
        inputComponent={MuiFaxInput}
        onChange={onChange}
      >
        {props.faxNumberError}
      </PhoneInput>
    </div>
  );
}

export { FaxNumberInput };
