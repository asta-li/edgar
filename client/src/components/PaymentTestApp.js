import React from 'react';
import Box from '@material-ui/core/Box';
import ReactDOM from "react-dom"

//THis file is just trying stuff out, not used in prod
function insertScriptElement({ url, attributes = {}, properties = {}, callback }) {
    const newScript = document.createElement('script');
    newScript.onerror = (err => console.error('An error occured while loading the PayPal JS SDK', err));
    if (callback) newScript.onload = callback;

    Object.keys(attributes).forEach(key => {
        newScript.setAttribute(key, attributes[key]);
    });

    document.head.appendChild(newScript);
    newScript.src = url;
}

const PaymentTestApp = props => {
    const [paid, setPaid] = React.useState(false);
    const [error, setError] = React.useState(null);
    const paypalContainerRef = React.useRef();
    const [_scriptLoaded, setScriptLoaded] = React.useState(false);

    const isFaxUploadSuccessful = props.isFaxUploadSuccessful;

    React.useEffect(() => {
        // check if PayPal JS SDK is already loaded
        if (window.paypal) {
            setScriptLoaded(true);
            renderButtons();
        } else {
            insertScriptElement({
                url: 'https://www.paypal.com/sdk/js?client-id=sb',
                callback: () => {
                    setScriptLoaded(true);
                    renderButtons();
                }
            })
        }
    }, []);


    const renderButtons = () => {

        window.paypal
            .Buttons({
                style: {
                    shape: "pill",
                    color: "blue",
                    layout: "horizontal",
                    label: "paypal",
                },
                funding: {
                    disallowed:[window.paypal.FUNDING.CREDIT, window.paypal.FUNDING.PAYLATER]
                },
                createOrder: (data, actions) => {
                    props.handleFileFax()
                    return actions.order.create({
                        intent: "CAPTURE",
                        purchase_units: [
                            {
                                description: "Your description",
                                amount: {
                                    currency_code: "USD",
                                    value: 1.0,
                                },
                            },
                        ],
                    });
                },
                onApprove: async (data, actions) => {
                    const order = await actions.order.capture();
                    setPaid(true);
                    // tell backend to check that order is approved and to fax the order out
                    console.log(order);
                },
                onError: (err) => {
                    //   setError(err),
                    console.error(err);
                },
            })
            .render(paypalContainerRef.current);
    };


    // If the payment has been made
    if (paid) {
        return <div>Payment successful!</div>;
    }

    // If any error occurs
    if (error) {
        return <div>Error Occurred in processing payment.! Please try again.</div>;
    }

    // Default Render
    return (
        <div ref={paypalContainerRef}>
            {
                isFaxUploadSuccessful === true ?
                    <div >
                        <Box border={1} onClick={() => console.log("pauypal div has been clicked")}>
                            <Box>this should only appear after person gets response for uploading fax back</Box>
                            <h4>Total Amount in Rs. : 500 /-</h4>
                        </Box>
                    </div>
                    :
                    <div></div>
            }
        </div>

    );
}

function createOrder() {
    return fetch('/my-server/create-paypal-transaction', {
        method: 'post',
        headers: {
            'content-type': 'application/json'
        }
    }).then(function(res) {
        return res.json();
    }).then(function(data) {
        return data.orderID; // Use the same key name for order ID on the client and server
    });
}

// let the server know the the payment has been processed


export default PaymentTestApp;
// export default withStyles(styles)(FaxMachineApp);