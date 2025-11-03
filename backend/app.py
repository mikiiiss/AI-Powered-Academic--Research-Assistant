
# # backend/app.py
# from flask import Flask
# from flask_cors import CORS


# def create_app() -> Flask:
#     app = Flask(__name__)
#     CORS(app, resources={r"/api/*": {"origins": "*"}})

#     # ------------------------------------------------------------------
#     # IMPORT BLUEPRINTS – using the exact variable names from each module
#     # ------------------------------------------------------------------
#     try:
#         from api.routes.citation_routes import citation_bp
#         from api.routes.evidence_routes import evidence_bp
#         from api.routes.gap_routes import gap_bp
#         from api.routes.paper_routes import paper_bp
#         from api.routes.recommendation_routes import rec_bp
#         from api.routes.trend_routes import trend_bp
#     except ImportError as e:
#         raise ImportError(
#             "One of the route modules could not be imported. "
#             "Verify that each file under backend/api/routes/ defines its blueprint "
#             "with the correct name (e.g., evidence_bp = Blueprint(...))."
#         ) from e

#     # Register them under /api (no url_prefix needed if routes already include /evidence, etc.)
#     app.register_blueprint(citation_bp, url_prefix="/api")
#     app.register_blueprint(evidence_bp, url_prefix="/api")
#     app.register_blueprint(gap_bp, url_prefix="/api")
#     app.register_blueprint(paper_bp, url_prefix="/api")
#     app.register_blueprint(rec_bp, url_prefix="/api")
#     app.register_blueprint(trend_bp, url_prefix="/api")

#     # ------------------------------------------------------------------
#     # Health endpoint (no DB needed)
#     # ------------------------------------------------------------------
#     @app.route("/api/health", methods=["GET"])
#     def health():
#         return {"status": "healthy", "message": "API is running"}, 200

#     return app


# # ----------------------------------------------------------------------
# # Run locally
# # ----------------------------------------------------------------------
# if __name__ == "__main__":
#     print("Starting Research Assistant API on http://0.0.0.0:5000")
#     app = create_app()
#     app.run(host="0.0.0.0", port=5000, debug=True)



# backend/app.py (UPDATED)
from flask import Flask
from flask_cors import CORS
import os

def create_app() -> Flask:
    app = Flask(__name__)
    
    # ✅ FIXED CORS - Allow all origins for testing
    CORS(app)  # This allows ALL origins
    
    # Import blueprints
    from api.routes.citation_routes import citation_bp
    from api.routes.evidence_routes import evidence_bp
    from api.routes.gap_routes import gap_bp
    from api.routes.paper_routes import paper_bp
    from api.routes.recommendation_routes import rec_bp
    from api.routes.trend_routes import trend_bp

    # ✅ FIXED: Register with correct URL prefixes
    app.register_blueprint(citation_bp, url_prefix="/api/citations")
    app.register_blueprint(evidence_bp, url_prefix="/api/evidence") 
    app.register_blueprint(gap_bp, url_prefix="/api/gaps")
    app.register_blueprint(paper_bp, url_prefix="/api/papers")
    app.register_blueprint(rec_bp, url_prefix="/api/recommendations")
    app.register_blueprint(trend_bp, url_prefix="/api/trends")

    @app.route("/api/health", methods=["GET"])
    def health():
        return {"status": "healthy", "message": "Research Assistant API is running"}, 200

    @app.route("/")
    def root():
        return {"message": "Research Assistant API", "version": "1.0.0"}

    return app

if __name__ == "__main__":
    print("🚀 Starting Research Assistant API on http://localhost:5000")
    app = create_app()
    app.run(host="localhost", port=5000, debug=True)  # Changed to localhost