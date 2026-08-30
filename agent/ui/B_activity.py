# import streamlit as st
# from datetime import date

# from api import get_activities


# def activity_page(user):

#     st.header("🔍 Activity")

#     st.caption("Your activity and your AI agent's actions.")

#     activities = get_activities(user["user_id"])
#     # print("ACTIVITIES FROM API:")
#     # print(activities)

#     if not activities:
#         st.info("No activity yet.")
#         return

#     # ---------------- Filters ----------------

#     col1, col2, col3 = st.columns([3, 1, 1])

#     with col1:
#         search_action = st.text_input(
#             "Search Action", placeholder="e.g. product searched, login..."
#         )

#     with col2:
#         start_date = st.date_input("From", value=None)

#     with col3:
#         end_date = st.date_input("To", value=None)

#     # ---------------- Apply filters ----------------

#     filtered_activities = []

#     for activity in activities:

#         action = activity.get("action", "UNKNOWN")
#         created_at = activity.get("createdAt", "")

#         # Action search
#         if search_action:
#             if search_action.lower() not in action.lower().replace("_", " "):
#                 continue

#         # Date filter
#         if created_at:

#             activity_date = date.fromisoformat(created_at[:10])

#             if start_date and activity_date < start_date:
#                 continue

#             if end_date and activity_date > end_date:
#                 continue

#         filtered_activities.append(activity)

#     if not filtered_activities:
#         st.info("No activities match your filters.")
#         return

#     # ---------------- Activity icons ----------------

#     action_icons = {
#         "USER_LOGIN": "🔑",
#         "USER_REGISTERED": "📝",
#         "PRODUCT_SEARCHED": "🔎",
#         "PRODUCT_VIEWED": "👁️",
#         "PRODUCT_CREATED": "➕",
#         "PRODUCT_UPDATED": "✏️",
#         "PRODUCT_DELETED": "🗑️",
#         "ORDER_CREATED": "🛒",
#         "PAYMENT_INITIATED": "💳",
#         "PAYMENT_SUCCESS": "✅",
#         "PAYMENT_FAILED": "❌",
#     }

#     # ---------------- Activity cards ----------------

#     for activity in filtered_activities:

#         actor = activity.get("actor_type", "USER")
#         action = activity.get("action", "UNKNOWN")
#         entity_type = activity.get("entity_type")
#         entity_id = activity.get("entity_id")
#         user_id = activity.get("user_id")
#         ip = activity.get("IP")
#         created_at = activity.get("createdAt")

#         icon = action_icons.get(action, "⚡")

#         if actor == "AGENT":
#             actor_label = "AI Agent"
#         else:
#             actor_label = "You"

#         #####################################################################
#         ## if u want to remove order history fetched by user:
#         # if action == "ORDER_HISTORY_FETCHED" and actor == "USER":
#         #     continue
#         #####################################################################

#         is_auth_activity = action in ["USER_LOGIN", "USER_REGISTERED"]

#         with st.container(border=True):

#             col1, col2, col3, col4 = st.columns([3, 2, 3, 2])

#             # Action
#             with col1:

#                 st.markdown(f"**{icon} {action.replace('_', ' ').title()}**")

#                 st.caption(actor_label)

#             if is_auth_activity:

#                 # User ID
#                 with col2:

#                     st.caption("User ID")

#                     if user_id:
#                         st.write(f"`{user_id}`")
#                     else:
#                         st.write("-")

#                 # IP
#                 with col3:

#                     st.caption("IP")

#                     if ip:
#                         st.write(f"`{ip}`")
#                     else:
#                         st.write("-")

#             else:

#                 # Entity Type
#                 with col2:

#                     st.caption("Entity Type")

#                     if entity_type:
#                         st.write(f"`{entity_type}`")
#                     else:
#                         st.write("-")

#                 # Entity ID
#                 with col3:

#                     st.caption("Entity ID")

#                     if entity_id:
#                         st.write(f"`{entity_id}`")
#                     else:
#                         st.write("-")

#             # Time
#             with col4:

#                 st.caption("Time")

#                 if created_at:
#                     st.write(created_at.replace("T", " ").split(".")[0])
#                 else:
#                     st.write("-")












import streamlit as st

from datetime import date

from api import get_activities


def activity_page(user):

    st.header("🔍 Activity")
    st.caption("Your activity and your AI agent's actions.")

    activities = get_activities(user["user_id"])

    if not activities:
        st.info("No activity yet.")
        return

    # ---------------- Filters ----------------

    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        search_action = st.text_input(
            "Search Action",
            placeholder="e.g. product searched, login..."
        )

    with col2:
        start_date = st.date_input(
            "From",
            value=None
        )

    with col3:
        end_date = st.date_input(
            "To",
            value=None
        )

    # ---------------- Apply filters ----------------

    filtered_activities = []

    for activity in activities:

        action = activity.get("action", "UNKNOWN")
        created_at = activity.get("createdAt", "")

        # Action search
        if search_action:
            if search_action.lower() not in action.lower().replace("_", " "):
                continue

        # Date filter
        if created_at:
            activity_date = date.fromisoformat(created_at[:10])

            if start_date and activity_date < start_date:
                continue

            if end_date and activity_date > end_date:
                continue

        filtered_activities.append(activity)

    if not filtered_activities:
        st.info("No activities match your filters.")
        return

    # ---------------- Activity icons ----------------

    action_icons = {

        # Authentication
        "USER_LOGIN": "🔑",
        "USER_REGISTERED": "📝",

        # Products
        "PRODUCT_SEARCHED": "🔎",
        "PRODUCT_VIEWED": "👁️",
        "PRODUCT_CREATED": "➕",
        "PRODUCT_UPDATED": "✏️",
        "PRODUCT_DELETED": "🗑️",

        # Cart
        "ADDED_ITEMS_IN_CART": "🛒",
        "CART_FETCHED": "📦",
        "CART_MODIFIED": "✏️",
        "ITEMS_REMOVED_FROM_CART": "➖",
        "CART_CLEARED": "🗑️",

        # Cart checkout / payment
        "CART_CHECKOUT_INITIATED": "💳",
        "CART_PAYMENT_CONFIRMED": "✅",

        # Orders
        "ORDER_CREATED": "🛍️",
        "ORDER_PAYMENT_VERIFIED": "💰",
        "ORDER_HISTORY_FETCHED": "📜",

        # Generic payment activities
        "PAYMENT_INITIATED": "💳",
        "PAYMENT_SUCCESS": "✅",
        "PAYMENT_FAILED": "❌",
    }

    # ---------------- Activity cards ----------------

    for activity in filtered_activities:

        actor = activity.get("actor_type", "USER")
        action = activity.get("action", "UNKNOWN")
        entity_type = activity.get("entity_type")
        entity_id = activity.get("entity_id")
        user_id = activity.get("user_id")
        ip = activity.get("IP")
        created_at = activity.get("createdAt")

        icon = action_icons.get(action, "⚡")

        if actor == "AGENT":
            actor_label = "AI Agent"
        else:
            actor_label = "You"

        # Authentication activities
        is_auth_activity = action in [
            "USER_LOGIN",
            "USER_REGISTERED"
        ]

        with st.container(border=True):

            col1, col2, col3, col4 = st.columns(
                [3, 2, 3, 2]
            )

            # ---------------- Action ----------------

            with col1:

                st.markdown(
                    f"**{icon} {action.replace('_', ' ').title()}**"
                )

                st.caption(actor_label)

            # ---------------- Authentication ----------------

            if is_auth_activity:

                # User ID
                with col2:

                    st.caption("User ID")

                    if user_id:
                        st.write(f"`{user_id}`")
                    else:
                        st.write("-")

                # IP
                with col3:

                    st.caption("IP")

                    if ip:
                        st.write(f"`{ip}`")
                    else:
                        st.write("-")

            # ---------------- Normal activities ----------------

            else:

                # Entity Type
                with col2:

                    st.caption("Entity Type")

                    if entity_type:
                        st.write(f"`{entity_type}`")
                    else:
                        st.write("-")

                # Entity ID
                with col3:

                    st.caption("Entity ID")

                    if entity_id:
                        st.write(f"`{entity_id}`")
                    else:
                        st.write("-")

            # ---------------- Time ----------------

            with col4:

                st.caption("Time")

                if created_at:

                    st.write(
                        created_at
                        .replace("T", " ")
                        .split(".")[0]
                    )

                else:
                    st.write("-")

