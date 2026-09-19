from flask import Flask, jsonify, render_template, request

from rag.rag_pipeline import RAGPipeline


app = Flask(__name__)


print("=" * 60)
print("SAKZ'S RESTAURANT AI")
print("=" * 60)
print("Initializing application...")


# =========================================================
# INITIALIZE RAG
# =========================================================

try:

    rag = RAGPipeline()

    rag_ready = True

    print("RAG system ready.")

except Exception as error:

    rag = None

    rag_ready = False

    print("RAG initialization failed.")
    print(f"Error: {error}")


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template("index.html")


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/api/health")
def health():

    return jsonify(
        {
            "status": "ok",
            "rag_ready": rag_ready,
            "restaurant": "Sakz's Restaurant"
        }
    )


# =========================================================
# CHAT
# =========================================================

@app.route("/api/chat", methods=["POST"])
def chat():

    print("\n" + "-" * 60)
    print("NEW CHAT REQUEST")

    # -----------------------------------------------------
    # CHECK RAG
    # -----------------------------------------------------

    if not rag_ready or rag is None:

        print("ERROR: RAG is not ready.")

        return jsonify(
            {
                "success": False,
                "error": (
                    "The restaurant AI is currently unavailable. "
                    "Please try again later."
                )
            }
        ), 503


    # -----------------------------------------------------
    # READ REQUEST
    # -----------------------------------------------------

    data = request.get_json(silent=True)

    if not data:

        print("ERROR: Invalid JSON request.")

        return jsonify(
            {
                "success": False,
                "error": "Invalid request."
            }
        ), 400


    question = data.get(
        "question",
        ""
    ).strip()


    print(f"Question: {question}")


    if not question:

        return jsonify(
            {
                "success": False,
                "error": "Please enter a question."
            }
        ), 400


    # -----------------------------------------------------
    # QUESTION LENGTH PROTECTION
    # -----------------------------------------------------

    if len(question) > 500:

        return jsonify(
            {
                "success": False,
                "error": "Question is too long."
            }
        ), 400


    # -----------------------------------------------------
    # RUN RAG
    # -----------------------------------------------------

    try:

        print("Running RAG...")

        result = rag.answer(question)

        print("RAG completed successfully.")

        print(
            f"Grounded: {result.get('grounded')}"
        )


        # -------------------------------------------------
        # FORMAT SOURCES
        # -------------------------------------------------

        sources = []

        for rank, source in enumerate(
            result.get("sources", []),
            start=1
        ):

            sources.append(
                {
                    "rank": rank,
                    "score": round(
                        float(source.get("score", 0)),
                        4
                    ),
                    "text": source.get(
                        "chunk",
                        ""
                    )
                }
            )


        print("Sending response to browser.")

        print("-" * 60)


        return jsonify(
            {
                "success": True,
                "answer": result.get(
                    "answer",
                    ""
                ),
                "grounded": result.get(
                    "grounded",
                    False
                ),
                "sources": sources
            }
        )


    # -----------------------------------------------------
    # EXPECTED AI SERVICE ERROR
    # -----------------------------------------------------

    except RuntimeError as error:

        print("AI SERVICE ERROR:")
        print(error)

        print("-" * 60)


        return jsonify(
            {
                "success": False,
                "error": str(error)
            }
        ), 503


    # -----------------------------------------------------
    # UNEXPECTED ERROR
    # -----------------------------------------------------

    except Exception as error:

        print("UNEXPECTED CHAT ERROR:")
        print(error)

        print("-" * 60)


        return jsonify(
            {
                "success": False,
                "error": (
                    "Something went wrong while processing "
                    "your question. Please try again."
                )
            }
        ), 500


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("SAKZ'S RESTAURANT AI SERVER")
    print("=" * 60)

    print(
        "Open: http://127.0.0.1:5000"
    )

    print("=" * 60)


    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        threaded=True
    )