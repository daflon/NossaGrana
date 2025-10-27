const { override, overrideDevServer } = require('customize-cra');

const devServerConfig = () => config => {
  config.setupMiddlewares = (middlewares, devServer) => {
    return middlewares;
  };
  
  delete config.onAfterSetupMiddleware;
  delete config.onBeforeSetupMiddleware;
  
  return config;
};

module.exports = {
  webpack: override(),
  devServer: overrideDevServer(devServerConfig())
};