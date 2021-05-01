// Returns empty string if the in-progress fax number is valid.
function validateFaxNumberInProgress(faxNumber) {
  let status = '';

  if (!faxNumber) {
    return status;
  }
  
  // Check the fax number length, which is 10 digits plus the US country code (+1)
  if (faxNumber.length > 12) {
    status = 'Fax number must be 10 digits long';
    return status ;
  }

  return status;
}

// Returns empty string if the fax number is valid.
function validateFaxNumber(faxNumber) {
  let status = '';
  
  if (!faxNumber) {
    status = 'Please enter a fax number';
    return status;
  }

  const inProgressStatus = validateFaxNumberInProgress(faxNumber);
  if (inProgressStatus) {
    return inProgressStatus;
  }

  if (faxNumber.length !== 12) {
    status = 'Fax number must be 10 digits long';
    return status ;
  }
  
  return status;
}

export {validateFaxNumberInProgress};
export {validateFaxNumber};
