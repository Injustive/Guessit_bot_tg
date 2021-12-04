CREATE_TABLE_QUERY = """
                        CREATE TABLE IF NOT EXISTS jwt_token_info (id serial PRIMARY KEY, 
                        user_id int NOT NULL UNIQUE, 
                        access varchar NOT NULL,
                        refresh varchar NOT NULL)
                    """

INSERT_OR_UPDATE_TOKEN_QUERY = """
            INSERT INTO jwt_token_info(user_id, access, refresh)
            VALUES ($1, $2, $3)
            ON CONFLICT(user_id) DO UPDATE SET access = $2, refresh = $3
        """

GET_TOKENS_QUERY = "SELECT refresh, access from jwt_token_info WHERE user_id = $1"

CLEAR_TOKENS_QUERY = "DELETE from jwt_token_info WHERE user_id = $1"

WRITE_ACCESS_TOKEN_QUERY = "UPDATE jwt_token_info SET access = $1 WHERE refresh = $2"
