import axios from 'axios';
import React from 'react';
import TextField from '@material-ui/core/TextField';

const QueryInput = props => {
    const handleKeyDown = (event) => {
        if (event.key === "Enter") {
            let query = event.target.value
            props.setResponse("Asking Edgar: " + query)

            let config = {
                params: {
                    "query": query
                }
            }
            // axios.get('/api', config)
            // axios.get('http://flask-env.eba-dwnhvhak.us-west-1.elasticbeanstalk.com/api', config)
            axios.get('http://127.0.0.1:5000/api', config)
            .then((response) => {
                console.log(response);
                props.setResponse(JSON.stringify(response.data))
            })
            .catch((error) => {
                console.log(error);
                props.setResponse("Sorry, I couldn't understand your question! I'm still learning.")
            })
            .then(() => {
                // always executed
                console.log("Hello world!");
            });
        }
    }

    return (
        <React.Fragment>
            <TextField
              id="query"
              fullWidth
              label="Type your question here"
              variant="outlined"
              onKeyDown={handleKeyDown}
            />
        </React.Fragment>
    );
}

export { QueryInput };