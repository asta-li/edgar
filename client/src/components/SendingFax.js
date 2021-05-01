import axios from "axios";
import CircularProgress from "@material-ui/core/CircularProgress";
import React from "react";
import Container from "@material-ui/core/Container";

const FAILED = 0;
const IN_PROGRESS = 1;
const SUCCESS = 2;

// callback to handling polling
// possible fax statues
//fax.queued
//fax.media.processed
//fax.sending.started
//fax.delivered
//fax.failed
const pollFaxStatus = (faxId, setFaxStatus) => {

    axios.get('/api/fax-status?', {
        params: {
            id: faxId
        }})
        .then((response) => {

            console.log('Received successful fax response', response.data);

            if (response.data.status === "delivered") {
                setFaxStatus(SUCCESS);
            } else if (response.data.status === "failed") {
                setFaxStatus(FAILED);
            } else {
                setFaxStatus(IN_PROGRESS);
                setTimeout(()=> {pollFaxStatus(faxId, setFaxStatus)}, 10000/*every 10 seconds*/);
            }
        })
        .catch((error) => {
            console.log("something went wrong querying fax status, will continue polling", error);
            setFaxStatus(IN_PROGRESS);
        });
};

const SendingFax =  (props) => {

    const [faxStatus, setFaxStatus] = React.useState(null);
    const [faxId, setFaxId] = React.useState(null);

    const headerConfig = {
        headers: { 'content-type': 'multipart/form-data' }
    };

    React.useEffect(() => {
        console.log("component updated, making an API call");

        const formData = new FormData();
        formData.append('transactionId', props.transactionId);

        setFaxStatus(IN_PROGRESS);
        // try to send fax. on the backend will validate that the person has indeed paid.
        axios.post('/api/fax', formData, headerConfig)
            .then((response) => {

                // TODO: get fax id out and poll
                console.log('Received successful fax response', response);

                setFaxId(response.data.FaxId);
                setFaxStatus(IN_PROGRESS);
                pollFaxStatus(response.data.FaxId, setFaxStatus)
            })
            .catch((error) => {
                console.log(error);
                setFaxStatus(FAILED)
            });
    }, []);

    let mainDiv;

    if (faxStatus === SUCCESS) {
        mainDiv = <div>
            <h3>yay sucesssfully faxed,  you're all done here! and your fax id is </h3>
            <h3>{faxId}</h3>
        </div>
    } else if (faxStatus === IN_PROGRESS) {
        mainDiv = <div>
            <h3>sending the fax . . . </h3>
            <h3>you can navigate away from this page, you will receive an email notification upon successful fax</h3>
            <CircularProgress />
        </div>
    } else if (faxStatus === FAILED) {
        mainDiv = <div>
            <h3>something went wrong with sending the fax. We will not charge you on unsuccesful faxes</h3>
        </div>
    }

    return (
        <Container maxWidth="sm">
            {mainDiv}
        </Container>
    )

}

export default SendingFax;