// @ts-nocheck
import { describe, it, expect } from 'vitest';
import express from 'express';
import { documentsRouter } from '../routes/documents';
import { notesRouter } from '../routes/notes';


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
  return res as unknown as express.Response & { body: unknown; statusCode: number };
}

describe('Document Routes', () => {
  describe('GET /api/documents', () => {
    it('returns empty array initially via handler', () => {
      const req = mockReq();
      const res = mockRes();

      documentsRouter.stack
        .find((layer: any) => layer.route?.path === '/' && layer.route?.methods?.get)
        ?.route?.stack[0]?.handle(req, res);

      expect(res.body).toEqual({ documents: expect.any(Array), total: expect.any(Number) });
    });
  });

  describe('POST /api/documents', () => {
    it('returns 400 when title is missing', () => {
      const req = mockReq({ body: { app_id: 'eodocs' } });
      const res = mockRes();

      const postHandler = documentsRouter.stack
        .find((layer: any) => layer.route?.path === '/' && layer.route?.methods?.post)
        ?.route?.stack[0]?.handle;

      postHandler(req, res);
      expect(res.statusCode).toBe(400);
    });

    it('returns 400 when app_id is missing', () => {
      const req = mockReq({ body: { title: 'Test Doc' } });
      const res = mockRes();

      const postHandler = documentsRouter.stack
        .find((layer: any) => layer.route?.path === '/' && layer.route?.methods?.post)
        ?.route?.stack[0]?.handle;

      postHandler(req, res);
      expect(res.statusCode).toBe(400);
    });

    it('creates a document with 201 status', () => {
      const req = mockReq({
        body: { title: 'My Doc', content: 'Body', app_id: 'eodocs', tags: ['work'] },
      });
      const res = mockRes();

      const postHandler = documentsRouter.stack
        .find((layer: any) => layer.route?.path === '/' && layer.route?.methods?.post)
        ?.route?.stack[0]?.handle;

      postHandler(req, res);
      expect(res.statusCode).toBe(201);
      const body = res.body as Record<string, unknown>;
      expect(body.id).toBeDefined();
      expect(body.title).toBe('My Doc');
      expect(body.content).toBe('Body');
      expect(body.app_id).toBe('eodocs');
      expect(body.tags).toEqual(['work']);
    });
  });

  describe('GET /api/documents/:id', () => {
    it('returns 404 for unknown id', () => {
      const req = mockReq({ params: { id: 'nonexistent-id' } });
      const res = mockRes();

      const getByIdHandler = documentsRouter.stack
        .find((layer: any) => layer.route?.path === '/:id' && layer.route?.methods?.get)
        ?.route?.stack[0]?.handle;

      getByIdHandler(req, res);
      expect(res.statusCode).toBe(404);
    });
  });

  describe('PUT /api/documents/:id', () => {
    it('returns 404 for unknown id', () => {
      const req = mockReq({
        params: { id: 'nonexistent-id' },
        body: { title: 'Updated' },
      });
      const res = mockRes();

      const putHandler = documentsRouter.stack
        .find((layer: any) => layer.route?.path === '/:id' && layer.route?.methods?.put)
        ?.route?.stack[0]?.handle;

      putHandler(req, res);
      expect(res.statusCode).toBe(404);
    });
  });

  describe('DELETE /api/documents/:id', () => {
    it('returns 404 for unknown id', () => {
      const req = mockReq({ params: { id: 'nonexistent-id' } });
      const res = mockRes();

      const deleteHandler = documentsRouter.stack
        .find((layer: any) => layer.route?.path === '/:id' && layer.route?.methods?.delete)
        ?.route?.stack[0]?.handle;

      deleteHandler(req, res);
      expect(res.statusCode).toBe(404);
    });
  });
});

describe('Note Routes', () => {
  describe('GET /api/notes', () => {
    it('returns notes array via handler', () => {
      const req = mockReq({ query: {} });
      const res = mockRes();

      notesRouter.stack
        .find((layer: any) => layer.route?.path === '/' && layer.route?.methods?.get)
        ?.route?.stack[0]?.handle(req, res);

      expect(res.body).toEqual({ notes: expect.any(Array), total: expect.any(Number) });
    });
  });

  describe('POST /api/notes', () => {
    it('returns 400 when title is missing', () => {
      const req = mockReq({ body: { content: 'No title' } });
      const res = mockRes();

      const postHandler = notesRouter.stack
        .find((layer: any) => layer.route?.path === '/' && layer.route?.methods?.post)
        ?.route?.stack[0]?.handle;

      postHandler(req, res);
      expect(res.statusCode).toBe(400);
    });

    it('creates a note with 201 status', () => {
      const req = mockReq({
        body: { title: 'My Note', content: 'Content', tags: ['test'], pinned: true },
      });
      const res = mockRes();

      const postHandler = notesRouter.stack
        .find((layer: any) => layer.route?.path === '/' && layer.route?.methods?.post)
        ?.route?.stack[0]?.handle;

      postHandler(req, res);
      expect(res.statusCode).toBe(201);
      const body = res.body as Record<string, unknown>;
      expect(body.id).toBeDefined();
      expect(body.title).toBe('My Note');
      expect(body.content).toBe('Content');
      expect(body.tags).toEqual(['test']);
      expect(body.pinned).toBe(true);
    });
  });

  describe('GET /api/notes/:id', () => {
    it('returns 404 for unknown id', () => {
      const req = mockReq({ params: { id: 'nonexistent-id' } });
      const res = mockRes();

      const getByIdHandler = notesRouter.stack
        .find((layer: any) => layer.route?.path === '/:id' && layer.route?.methods?.get)
        ?.route?.stack[0]?.handle;

      getByIdHandler(req, res);
      expect(res.statusCode).toBe(404);
    });
  });

  describe('DELETE /api/notes/:id', () => {
    it('returns 404 for unknown id', () => {
      const req = mockReq({ params: { id: 'nonexistent-id' } });
      const res = mockRes();

      const deleteHandler = notesRouter.stack
        .find((layer: any) => layer.route?.path === '/:id' && layer.route?.methods?.delete)
        ?.route?.stack[0]?.handle;

      deleteHandler(req, res);
      expect(res.statusCode).toBe(404);
    });
  });
});
