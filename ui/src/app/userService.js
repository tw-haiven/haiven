"use client";

import jwt from "jsonwebtoken";

const userService = {
  getSessionCookie() {
    if (typeof document !== "undefined" && document.cookie) {
      return document?.cookie
        ?.split("; ")
        .find((row) => row.startsWith("session="))
        .split("=")[1];
    }
    return null;
  },

  decodeJWT(token) {
    try {
      return jwt.decode(token);
    } catch (error) {
      console.error("Failed to decode JWT", error);
      return null;
    }
  },

  getName() {
    const token = this.getSessionCookie();
    const decoded = this.decodeJWT(token);
    return decoded ? decoded.user.name : null;
  },

  getProfilePicture() {
    const token = this.getSessionCookie();
    const decoded = this.decodeJWT(token);
    return decoded ? decoded.user.picture : null;
  },
};

export default userService;
