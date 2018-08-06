"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.brewHook = async function () {
    this.config.runHook('recache', { type: 'update' });
};
