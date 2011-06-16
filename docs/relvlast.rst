JVS2
====


Graph of the Persistent Object Tree
-----------------------------------

.. digraph:: root

  Root -> "translations[locale]" -> Language;
  Root -> properties -> Properties;

  Language -> locale;
  Language -> words -> VersionedObjects;
  Language -> pages -> VersionedObjects;

  Properties -> words -> VersionedObjects;

  VersionedObjects -> "save(name, object)";
  VersionedObjects -> "latest(name)" -> Object;
  VersionedObjects -> "[name]" -> List;

  List -> last -> Version;
  List -> "[id]" -> Version;

  Version -> timestamp;
  Version -> object -> Object;

  Object -> Translation;
  Object -> Page;
  Object -> WordProperties;

  Translation -> of;
  Translation -> definition;
  Translation -> notes;

  Page -> title;
  Page -> body;

  WordProperties -> id;
  WordProperties -> type;
  WordProperties -> class_;
  WordProperties -> affixes;
