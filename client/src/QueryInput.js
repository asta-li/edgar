import axios from 'axios';
import React from 'react';
import TextField from '@material-ui/core/TextField';

const QueryInput = props => {
    const handleKeyDown = (event) => {
        if (event.key === "Enter") {
            let query = event.target.value
            props.setResponse("Asking Edgar...")
            
            // Short-circuit likely-invalid queries.
            if (query.length < 15) {
                props.setResponse("Sorry, I couldn't understand your question.")
                return
            }

            // Query the API with the user input.
            let config = {
                params: {
                    "query": query
                }
            }
    
            axios.get('http://127.0.0.1:5000/api', config)
            // axios.get('/api', config)
            // axios.get('http://flask-env.eba-dwnhvhak.us-west-1.elasticbeanstalk.com/api', config)
            .then((response) => {
                console.log(response);
                if (!response.data.status.valid) {
                    throw new Error("API query failed.");
                }
                props.setResponse(response.data.data)
            })
            .catch((error) => {
                console.log(error);
                props.setResponse("Sorry, I couldn't understand your question! I'm still learning.")
            })
        }
    }

    return (
        <React.Fragment>
            <TextField
              id="query"
              fullWidth
              label="Ask me a question."
              variant="outlined"
              onKeyDown={handleKeyDown}
            />
        </React.Fragment>
    );
}

export { QueryInput };