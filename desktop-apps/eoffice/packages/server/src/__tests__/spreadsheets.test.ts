// @ts-nocheck
import { describe, it, expect } from 'vitest';
import express from 'express';
import { spreadsheetsRouter } from '../routes/spreadsheets';

function mockReq(overrides: Record<string, unknown> = {}) {
  return {
    params: {},
    query: {},
    body: {},
    ...overrides,
  } as unknown as express.Request;
}

function mockRes() {
  const res: Record<string, unknown> = {};
  res.status = (code: number) => {
    res.statusCode = code;
    return res;
  };
  res.json = (data: unknown) => {
    res.body = data;
    return res;
  };
  res.send = () => res;
  res.statusCode = 200;
  return res as unknown as express.Response & {
    body: unknown;
    statusCode: number;
  };
}

function findHandler(
  method: 'get' | 'post' | 'put' | 'delete',
  path: string,
) {
  return spreadsheetsRouter.stack.find(
    (layer: any) =>
      layer.route?.path === path && layer.route?.methods?.[method],
  )?.route?.stack[0]?.handle;
}

describe('Spreadsheet Routes', () => {
  describe('GET /', () => {
    it('returns spreadsheets array', () => {
      const req = mockReq();
      const res = mockRes();
      findHandler('get', '/')(req, res);
      expect(res.body).toEqual({
        spreadsheets: expect.any(Array),
        total: expect.any(Number),
      });
    });
  });

  describe('POST /', () => {
    it('returns 400 when title is missing', () => {
      const req = mockReq({ body: {} });
      const res = mockRes();
      findHandler('post', '/')(req, res);
      expect(res.statusCode).toBe(400);
    });

    it('creates a spreadsheet with 201 status', () => {
      const req = mockReq({ body: { title: 'My Spreadsheet' } });
      const res = mockRes();
      findHandler('post', '/')(req, res);
      expect(res.statusCode).toBe(201);
      const body = res.body as Record<string, unknown>;
      expect(body.id).toBeDefined();
      expect(body.title).toBe('My Spreadsheet');
      expect(body.sheets).toEqual(expect.any(Array));
      expect((body.sheets as any[]).length).toBe(1);
    });
  });

  describe('GET /:id', () => {
    it('returns 404 for unknown id', () => {
      const req = mockReq({ params: { id: 'nonexistent-id' } });
      const res = mockRes();
      findHandler('get', '/:id')(req, res);
      expect(res.statusCode).toBe(404);
    });

    it('returns a previously created spreadsheet', () => {
      const createReq = mockReq({ body: { title: 'Fetch Test' } });
      const createRes = mockRes();
      findHandler('post', '/')(createReq, createRes);
      const created = createRes.body as Record<string, unknown>;

      const getReq = mockReq({ params: { id: created.id } });
      const getRes = mockRes();
      findHandler('get', '/:id')(getReq, getRes);
      expect(getRes.statusCode).toBe(200);
      expect((getRes.body as Record<string, unknown>).title).toBe(
        'Fetch Test',
      );
    });
  });

  describe('PUT /:id', () => {
    it('returns 404 for unknown id', () => {
      const req = mockReq({
        params: { id: 'nonexistent-id' },
        body: { title: 'Updated' },
      });
      const res = mockRes();
      findHandler('put', '/:id')(req, res);
      expect(res.statusCode).toBe(404);
    });

    it('updates the spreadsheet title', () => {
      const createReq = mockReq({ body: { title: 'Original' } });
      const createRes = mockRes();
      findHandler('post', '/')(createReq, createRes);
      const created = createRes.body as Record<string, unknown>;

      const putReq = mockReq({
        params: { id: created.id },
        body: { title: 'Updated Title' },
      });
      const putRes = mockRes();
      findHandler('put', '/:id')(putReq, putRes);
      expect(putRes.statusCode).toBe(200);
      expect((putRes.body as Record<string, unknown>).title).toBe(
        'Updated Title',
      );
    });
  });

  describe('DELETE /:id', () => {
    it('returns 404 for unknown id', () => {
      const req = mockReq({ params: { id: 'nonexistent-id' } });
      const res = mockRes();
      findHandler('delete', '/:id')(req, res);
      expect(res.statusCode).toBe(404);
    });

    it('deletes a spreadsheet with 204 status', () => {
      const createReq = mockReq({ body: { title: 'To Delete' } });
      const createRes = mockRes();
      findHandler('post', '/')(createReq, createRes);
      const created = createRes.body as Record<string, unknown>;

      const delReq = mockReq({ params: { id: created.id } });
      const delRes = mockRes();
      findHandler('delete', '/:id')(delReq, delRes);
      expect(delRes.statusCode).toBe(204);
    });
  });

  describe('PUT /:id/cells', () => {
    it('returns 404 for unknown spreadsheet', () => {
      const req = mockReq({
        params: { id: 'nonexistent-id' },
        body: { sheetId: 'abc', cells: [] },
      });
      const res = mockRes();
      findHandler('put', '/:id/cells')(req, res);
      expect(res.statusCode).toBe(404);
    });

    it('returns 400 when sheetId or cells are missing', () => {
      const createReq = mockReq({ body: { title: 'Cell Test' } });
      const createRes = mockRes();
      findHandler('post', '/')(createReq, createRes);
      const created = createRes.body as Record<string, unknown>;

      const req = mockReq({ params: { id: created.id }, body: {} });
      const res = mockRes();
      findHandler('put', '/:id/cells')(req, res);
      expect(res.statusCode).toBe(400);
    });
  });

  describe('POST /:id/sheets', () => {
    it('returns 400 when name is missing', () => {
      const createReq = mockReq({ body: { title: 'Sheet Test' } });
      const createRes = mockRes();
      findHandler('post', '/')(createReq, createRes);
      const created = createRes.body as Record<string, unknown>;

      const req = mockReq({ params: { id: created.id }, body: {} });
      const res = mockRes();
      findHandler('post', '/:id/sheets')(req, res);
      expect(res.statusCode).toBe(400);
    });

    it('adds a new sheet with 201 status', () => {
      const createReq = mockReq({ body: { title: 'Add Sheet Test' } });
      const createRes = mockRes();
      findHandler('post', '/')(createReq, createRes);
      const created = createRes.body as Record<string, unknown>;

      const req = mockReq({
        params: { id: created.id },
        body: { name: 'Sheet 2' },
      });
      const res = mockRes();
      findHandler('post', '/:id/sheets')(req, res);
      expect(res.statusCode).toBe(201);
      expect((res.body as Record<string, unknown>).name).toBe('Sheet 2');
    });
  });

  describe('DELETE /:id/sheets/:sheetId', () => {
    it('returns 400 when trying to delete the last sheet', () => {
      const createReq = mockReq({ body: { title: 'Last Sheet Test' } });
      const createRes = mockRes();
      findHandler('post', '/')(createReq, createRes);
      const created = createRes.body as Record<string, unknown>;
      const sheetId = (created.sheets as any[])[0].id;

      const req = mockReq({
        params: { id: created.id, sheetId },
      });
      const res = mockRes();
      findHandler('delete', '/:id/sheets/:sheetId')(req, res);
      expect(res.statusCode).toBe(400);
    });
  });
});
