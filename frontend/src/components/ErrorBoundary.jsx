import React from 'react';

/**
 * Standard React Error Boundary preventing application white-screen crashes.
 */
export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an UI error:", error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.hash = '#/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary-container" role="alert">
          <h2 className="error-title">Command Center Interface Error</h2>
          <p className="error-text">
            An unexpected error interrupted the operational dashboard view. 
            The backend service remains active and unaffected.
          </p>
          <button className="btn-primary" onClick={this.handleReset}>
            Recover Command Center
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
