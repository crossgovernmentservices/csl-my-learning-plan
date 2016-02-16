source ./environment-private.sh 2>/dev/null
export SETTINGS='application.config.DevelopmentConfig'
export SASS_PATH='.'
export SECRET_KEY='local-dev-not-secret'
export SECURITY_PASSWORD_HASH='bcrypt'
export MONGO_URI='mongodb://localhost:27017/mlp'
export DGN_RULE='learning_registry_match'
export LRS_QUERY_URL='/api/v1/statements/aggregate?pipeline=%s'
export LRS_STATEMENTS_URL='/data/xAPI/statements'
