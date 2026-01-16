from flask import Blueprint, request, jsonify

from app.services.journal_service import (
    add_journal, update_journal_by_id, delete_journal_by_id,
    close_trade_by_id, list_journals_filtered, 
    )

journal_bp = Blueprint("journal", __name__, url_prefix="/journals")


@journal_bp.route("", methods=["POST"])
def create_journal():
    data = request.get_json()
    
    # ⚠️ 现在先临时写死 user_id（后面会用 auth token）
    user_id = data.get("user_id")

    symbol = data.get("symbol")
    side = data.get("side")
    price = data.get("price")
    quantity = data.get("quantity")
    note = data.get("note")

    if not all([user_id, symbol, side, price, quantity]):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        journal_id = add_journal(
            user_id=user_id,
            symbol=symbol,
            side=side,
            price=price,
            quantity=quantity,
            note=note,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"message": "Journal created successfully", "journal_id": journal_id}), 201


 


@journal_bp.route("/<int:journal_id>", methods=["PUT"])
def update_journal(journal_id):
    data = request.get_json()

    user_id = data.get("user_id")  # 现在先这样，后面换 auth token
    symbol = data.get("symbol")
    side = data.get("side")
    price = data.get("price")
    quantity = data.get("quantity")
    note = data.get("note")

    if not all([user_id, symbol, side, price, quantity]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        update_journal_by_id(
            user_id=user_id,
            journal_id=journal_id,
            symbol=symbol,
            side=side,
            price=price,
            quantity=quantity,
            note=note,
        )
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"message": "Journal updated successfully"}), 200


@journal_bp.route("/<int:journal_id>", methods=["DELETE"])
def delete_journal(journal_id):
    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    try:
        delete_journal_by_id(user_id=user_id, journal_id=journal_id)
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    return jsonify({"message": "Journal deleted successfully"}), 200


@journal_bp.route("/<int:journal_id>/close", methods=["POST"])
def close_trade(journal_id):
    data = request.get_json()
    user_id = data.get("user_id")  # 先这样，后面换 token
    exit_price = data.get("exit_price")

    if not user_id or not exit_price:
        return jsonify({"error": "user_id and exit_price required"}), 400

    try:
        pnl = close_trade_by_id(
            user_id=user_id,
            journal_id=journal_id,
            exit_price=exit_price
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({
        "message": "Trade closed",
        "pnl": pnl
    })
    

@journal_bp.route("", methods=["GET"])
def get_journals():
    user_id = request.args.get("user_id", type=int)
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    symbol = request.args.get("symbol")
    status = request.args.get("status")          # open/closed
    start_date = request.args.get("start_date")  # YYYY-MM-DD
    end_date = request.args.get("end_date")      # YYYY-MM-DD
    side = request.args.get("side")              # buy/sell

    try:
        rows = list_journals_filtered(
            user_id=user_id,
            symbol=symbol,
            status=status,
            start_date=start_date,
            end_date=end_date,
            side=side,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # 记得这里的下标要和 SELECT 字段顺序一致
    result = []
    for r in rows:
        result.append({
            "journal_id": r[0],
            "user_id": r[1],
            "symbol": r[2],
            "side": r[3],
            "price": r[4],
            "quantity": r[5],
            "note": r[6],
            "exit_price": r[7],
            "exit_time": r[8],
            "pnl": r[9],
            "created_at": r[10],
        })

    return jsonify(result), 200
