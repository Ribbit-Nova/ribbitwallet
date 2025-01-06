# Ribbit Wallet

## Introduction
RibbitWallet is a secure and user-friendly cryptocurrency wallet application.

## Features
- Secure storage of cryptocurrencies
- User-friendly interface
- Fast transactions
- Support for multiple cryptocurrencies
- Integration with FastAPI backend

## Installation
To install RibbitWallet, follow these steps:
1. Clone the repository: `git clone https://github.com/Ribbit-Nova/ribbitwallet.git`
2. Navigate to the project directory: `cd ribbitwallet`

### Python Dependencies
Make sure you have Python installed. Then, install the required Python packages:
```
pip install -r requirements.txt
```

### FastAPI
RibbitWallet uses FastAPI for the backend. Ensure you have FastAPI installed:
```
pip install fastapi
pip install uvicorn
```

### Environment Variables
RibbitWallet requires certain environment variables to be set. You can find a sample environment file named `dev.env` in the repository. To use it, copy the `dev.env` file to `.env`:
```
cp dev.env .env
```
Make sure to update the values in the `.env` file as per your setup.

### Running the Application Locally
To run RibbitWallet locally without Docker, follow these steps:
1. Ensure you have all dependencies installed as mentioned in the Installation section.
2. Start the FastAPI server:
```
uvicorn app.main:app --reload
```

### Running the Applicationn via Docker
To run RibbitWallet using Docker, follow these steps:
1. Build the Docker image: `docker build -t ribbitwallet .`
2. Run the Docker container: `docker run -p 8000:8000 ribbitwallet`

## Usage
To start the application, run:
```
docker-compose up
```
Follow the on-screen instructions to set up your wallet and start managing your cryptocurrencies.

### API URL
The base URL for accessing the RibbitWallet API is:
```
http://localhost:8000/
```

### API Documentation

RibbitWallet provides API documentation using Swagger. Once the application is running, you can access the Swagger UI at `http://localhost:8000/redoc`. This interface allows you to explore and test the API endpoints interactively.

### Repository Structure
- `app/`: Contains the main application code.
- `configs/`: Contains the database and logging configurations.
- `docker-compose.yml`: The docker-compose.yml file defines and runs multi-container Docker applications.
- `Dockerfile`: A Dockerfile is a script containing a series of instructions on how to build a Docker image.
- `postman`: The postman folder contains Postman collections and environment variables.
- `.gitignore`: Specifies files and directories that should be ignored by Git.

## Notes

### Encryption and Decryption Steps

RibbitWallet uses AES-GCM encryption to securely store and manage your cryptocurrency keys and sensitive data. Follow these steps for encryption and decryption:

1. **Set the SECRET_KEY**: Ensure you have a `SECRET_KEY` defined in your `.env` file for encryption and decryption. Use the same key in your frontend application to maintain consistency.
   
   Example `.env` entry:
   ```
   SECRET_KEY=your_secret_key_here
   ```

2. **Encrypt Data**: Use the `SECRET_KEY` to encrypt your data. After encryption, convert the encrypted object to a base64 string.

3. **Send Encrypted Data**: Map the base64 string in your API request to securely transmit the encrypted data.

4. **Decrypt Data**: Decode the base64 string to get the encrypted data. After decode on the receiving end, Use the `SECRET_KEY` to decrypt the data back to its original form

By following these steps, you can ensure that your sensitive data is securely encrypted and decrypted within RibbitWallet.

### JWT Authentication

RibbitWallet uses JWT (JSON Web Tokens) for authentication and authorization. Follow these steps to set up and use JWT in your application:

1. **Set the JWT_SECRET_KEY**: Ensure you have a `JWT_SECRET_KEY` defined in your `.env` file for signing the JWT tokens.

    Example `.env` entry:
    ```
    JWT_SECRET_KEY=your_jwt_secret_key_here
    ```

2. **Generate JWT Token**: When a user logs in, generate a JWT token using the `JWT_SECRET_KEY`. This token will be used to authenticate subsequent requests.

3. **Send JWT Token**: Include the generated JWT token in the `Authorization` header of your API requests.

    Example header:
    ```
    Authorization: Bearer your_jwt_token_here
    ```

4. **Verify JWT Token**: On the server side, verify the JWT token in the `Authorization` header of incoming requests to ensure the user is authenticated.

By following these steps, you can implement secure authentication and authorization in RibbitWallet using JWT tokens.

### Code Style
We follow PEP 8 for Python code style. Please ensure your code adheres to these guidelines before submitting a pull request.

## Contributing
We welcome contributions to RibbitWallet. To contribute, follow these steps:
1. Fork the repository
2. Create a new branch: `git checkout -b feature-branch`
3. Make your changes and commit them: `git commit -m 'Add new feature'`
4. Push to the branch: `git push origin feature-branch`
5. Create a pull request

## Contact Information
For any questions or support, please contact us at support@ribbitwallet.com.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
