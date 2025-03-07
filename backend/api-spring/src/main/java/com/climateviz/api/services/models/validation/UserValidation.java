package com.climateviz.api.services.models.validation;

import com.climateviz.api.persistence.entities.UserEntity;
import com.climateviz.api.services.models.dtos.ResponseDTO;

public class UserValidation {
    public ResponseDTO validate(UserEntity user) {
        ResponseDTO response = new ResponseDTO();
        response.setNumOfErrors(0);
        if (user.getFirstName() == null
            // user.getFirstName().length() < 3 ||
            // user.getFirstName().length() > 15
        ) {
            response.setNumOfErrors(response.getNumOfErrors() + 1);
            // response.setMessage("The firstName field cannot be null, and field must be between 3 and 15 characters ");
            response.setMessage("The firstName field cannot be null");
        }
        if (user.getLastName() == null) {
            response.setNumOfErrors(response.getNumOfErrors() + 1);
            response.setMessage("The lastName field cannot be null");
        }

        if (user.getEmail() == null ||
                !user.getEmail().matches("^[\\w-\\.]+@([\\w-]+\\.)+[\\w-]{2,4}$")) {
            response.setNumOfErrors(response.getNumOfErrors() + 1);
            response.setMessage("The email field is not valid");
        }

        if (user.getPassword() == null ||
                !user.getPassword().matches("^(?=.*\\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z]).{8,16}$")
        ) {
            response.setNumOfErrors(response.getNumOfErrors() + 1);
            response.setMessage("The password must be between 8 and 16, at least one number, one lowercase letter and one uppercase letter.");
        }

        return response;
    }
}
