import { DeckGL } from "@deck.gl/react";
import { TileLayer } from "@deck.gl/geo-layers";
import { BitmapLayer, GeoJsonLayer } from "@deck.gl/layers";
import { useEffect, useMemo, useState } from "react";

import { useAppSelector } from "../store";

const INITIAL_VIEW_STATE = {
  longitude: -98,
  latitude: 39,
  zoom: 3,
  pitch: 0,
  bearing: 0,
};

// Open base tiles rendered through deck.gl's WebGL TileLayer.
function baseLayer() {
  return new TileLayer({
    id: "osm",
    data: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    minZoom: 0,
    maxZoom: 19,
    tileSize: 256,
    renderSubLayers: (props: any) => {
      const { west, south, east, north } = props.tile.bbox;
      return new BitmapLayer(props, {
        data: undefined,
        image: props.data,
        bounds: [west, south, east, north],
      });
    },
  });
}

export default function MapView() {
  const result = useAppSelector((s) => s.session.result);
  const [viewState, setViewState] = useState<Record<string, number>>(INITIAL_VIEW_STATE);
  const [detections, setDetections] = useState<unknown | null>(null);
  const [overlayOpacity, setOverlayOpacity] = useState(0);

  const overlay = result?.artifacts.find((a) => a.role === "change" || a.role === "ndvi");
  const geojsonUrl = result?.artifacts.find((a) => a.kind === "geojson")?.url;

  // Fly to the AOI and animate overlays in whenever a new result arrives.
  useEffect(() => {
    if (!result?.bbox) return;
    const [w, s, e, n] = result.bbox;
    setViewState({
      longitude: (w + e) / 2,
      latitude: (s + n) / 2,
      zoom: 10,
      pitch: 0,
      bearing: 0,
    });
    setOverlayOpacity(0);
    const t = setTimeout(() => setOverlayOpacity(0.75), 50);
    return () => clearTimeout(t);
  }, [result]);

  useEffect(() => {
    if (!geojsonUrl) {
      setDetections(null);
      return;
    }
    let active = true;
    fetch(geojsonUrl)
      .then((r) => r.json())
      .then((data) => active && setDetections(data))
      .catch(() => active && setDetections(null));
    return () => {
      active = false;
    };
  }, [geojsonUrl]);

  const layers = useMemo(() => {
    const ls: unknown[] = [baseLayer()];
    if (overlay && result?.bbox) {
      const [w, s, e, n] = result.bbox;
      ls.push(
        new BitmapLayer({
          id: `overlay-${overlay.url}`,
          image: overlay.url,
          bounds: [w, s, e, n],
          opacity: overlayOpacity,
          transitions: { opacity: 800 },
        }),
      );
    }
    if (detections) {
      ls.push(
        new GeoJsonLayer({
          id: "detections",
          data: detections as any,
          filled: true,
          stroked: true,
          getFillColor: [0, 220, 120, 90],
          getLineColor: [0, 255, 160, 220],
          lineWidthMinPixels: 1,
          transitions: { getFillColor: 600 },
        }),
      );
    }
    return ls;
  }, [overlay, detections, overlayOpacity, result]);

  return (
    <div className="map">
      <DeckGL
        viewState={viewState}
        controller={true}
        layers={layers as any}
        onViewStateChange={(e: any) => setViewState(e.viewState)}
      />
      <div className="attribution">© OpenStreetMap contributors</div>
    </div>
  );
}
